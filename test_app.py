import io
import re
import unittest
import zipfile
from app import app, GATEWAY_API_KEY, FLAG_SECRET, FLAG_WAF_BYPASS


class TestSmartFactoryGatewayExam(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.forbidden_words = ["vulnerable", "lab", "owasp", "hacking"]

    def _assert_no_forbidden_words(self, content: str, source_name: str):
        for word in self.forbidden_words:
            match = re.search(rf"\b{word}\b", content, re.IGNORECASE)
            self.assertIsNone(
                match, f"Forbidden word '{word}' found in {source_name}"
            )

    def test_01_landing_page_and_no_hints(self):
        """Ensure landing page has required title, button, and NO forbidden words."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        self.assertIn(
            "Smart Factory Gateway - PT Industri Otomasi Sejahtera", html
        )
        self.assertIn("Download Teknisi Mobile App (Android Source)", html)
        self._assert_no_forbidden_words(html, "index.html")

    def test_02_download_mobile_app_in_memory_zip(self):
        """Ensure /download/mobile-app dynamically serves a ZIP with AndroidManifest.xml and strings.xml."""
        res = self.client.get("/download/mobile-app")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, "application/zip")

        zip_bytes = io.BytesIO(res.data)
        self.assertTrue(zipfile.is_zipfile(zip_bytes))

        with zipfile.ZipFile(zip_bytes, "r") as zf:
            namelist = zf.namelist()
            self.assertIn("AndroidManifest.xml", namelist)
            self.assertIn("strings.xml", namelist)

            manifest_content = zf.read("AndroidManifest.xml").decode("utf-8")
            strings_content = zf.read("strings.xml").decode("utf-8")

            self.assertIn('android:exported="true"', manifest_content)
            self.assertIn(
                '<string name="gateway_api_key">IOS_FACTORY_SECRET_9912</string>',
                strings_content,
            )

            self._assert_no_forbidden_words(
                manifest_content, "AndroidManifest.xml"
            )
            self._assert_no_forbidden_words(strings_content, "strings.xml")

    def test_03_gateway_login_flow(self):
        """Verify /gateway-login rejects wrong key and redirects to /scada-panel on valid key."""
        res_get = self.client.get("/gateway-login")
        self.assertEqual(res_get.status_code, 200)
        html_get = res_get.get_data(as_text=True)
        self.assertIn("Gateway API Key", html_get)
        self._assert_no_forbidden_words(html_get, "gateway_login.html")

        # Invalid API key
        res_bad = self.client.post(
            "/gateway-login", data={"gateway_api_key": "WRONG_KEY_123"}
        )
        self.assertEqual(res_bad.status_code, 200)
        self.assertIn("Otorisasi Ditolak", res_bad.get_data(as_text=True))

        # Valid API key from strings.xml
        res_ok = self.client.post(
            "/gateway-login", data={"gateway_api_key": GATEWAY_API_KEY}
        )
        self.assertEqual(res_ok.status_code, 302)
        self.assertIn("/scada-panel", res_ok.headers["Location"])

    def test_04_scada_panel_requires_session_and_override_login(self):
        """Verify /scada-panel protection and SCADA Override Login default credentials."""
        # Unauthenticated access should redirect to /gateway-login
        res_unauth = self.client.get("/scada-panel")
        self.assertEqual(res_unauth.status_code, 302)
        self.assertIn("/gateway-login", res_unauth.headers["Location"])

        # Authenticate at gateway
        self.client.post(
            "/gateway-login", data={"gateway_api_key": GATEWAY_API_KEY}
        )

        # Initial access to /scada-panel shows SCADA Override Login
        res_locked = self.client.get("/scada-panel")
        self.assertEqual(res_locked.status_code, 200)
        html_locked = res_locked.get_data(as_text=True)
        self.assertIn("SCADA Override Login", html_locked)
        self.assertNotIn("IoT Sensor Firmware Update", html_locked)
        self._assert_no_forbidden_words(
            html_locked, "scada_panel.html (locked)"
        )

        # Login with default OT credentials (admin / password)
        res_override = self.client.post(
            "/scada-panel",
            data={
                "action": "scada_override",
                "username": "admin",
                "password": "password",
            },
        )
        self.assertEqual(res_override.status_code, 200)
        html_unlocked = res_override.get_data(as_text=True)
        self.assertIn("Suhu Mesin Utama", html_unlocked)
        self.assertIn("Tekanan Air Pendingin", html_unlocked)
        self.assertIn("IoT Sensor Firmware Update", html_unlocked)
        self._assert_no_forbidden_words(
            html_unlocked, "scada_panel.html (unlocked)"
        )

    def test_05_scada_override_accepts_admin_admin(self):
        """Verify SCADA Override also accepts admin / admin."""
        self.client.post(
            "/gateway-login", data={"gateway_api_key": GATEWAY_API_KEY}
        )
        res_override = self.client.post(
            "/scada-panel",
            data={
                "action": "scada_override",
                "username": "admin",
                "password": "admin",
            },
        )
        self.assertEqual(res_override.status_code, 200)
        self.assertIn(
            "IoT Sensor Firmware Update", res_override.get_data(as_text=True)
        )

    def test_06_firmware_update_normal_and_mocked_command_injection(self):
        """Verify normal firmware deployment and mocked Command Injection responses."""
        self.client.post(
            "/gateway-login", data={"gateway_api_key": GATEWAY_API_KEY}
        )
        self.client.post(
            "/scada-panel",
            data={
                "action": "scada_override",
                "username": "admin",
                "password": "password",
            },
        )

        # Normal input: v2.1
        res_normal = self.client.post(
            "/scada-panel",
            data={"action": "firmware_update", "firmware_version": "v2.1"},
        )
        self.assertEqual(res_normal.status_code, 200)
        html_normal = res_normal.get_data(as_text=True)
        self.assertIn(
            "Firmware v2.1 successfully deployed to sensors.", html_normal
        )
        self.assertNotIn(FLAG_SECRET, html_normal)

        # Mocked Command Injection payloads (; | && with whoami, ls, cat)
        injection_payloads = [
            "v2.1; whoami",
            "v2.1 | ls",
            "v2.1 && cat flag.txt",
            "v2.1; cat /etc/passwd",
        ]
        for payload in injection_payloads:
            res_inj = self.client.post(
                "/scada-panel",
                data={
                    "action": "firmware_update",
                    "firmware_version": payload,
                },
            )
            self.assertEqual(res_inj.status_code, 200)
            html_inj = res_inj.get_data(as_text=True)
            self.assertIn(
                f"root@scada-system:~# {FLAG_SECRET}",
                html_inj,
                f"Failed to return flag for payload: {payload}",
            )

    def test_07_firmware_update_waf_evasion_obfuscation(self):
        """Verify Linux Command Obfuscation (WAF Evasion) patterns return bonus flag."""
        self.client.post(
            "/gateway-login", data={"gateway_api_key": GATEWAY_API_KEY}
        )
        self.client.post(
            "/scada-panel",
            data={
                "action": "scada_override",
                "username": "admin",
                "password": "password",
            },
        )

        waf_evasion_payloads = [
            "v2.1; c''at flag.txt",
            "v2.1 | c\\at /etc/passwd",
            'v2.1 && c""at flag.txt',
            "v2.1; /bin/?at flag.txt",
            "c''at flag.txt",
        ]
        for payload in waf_evasion_payloads:
            res_waf = self.client.post(
                "/scada-panel",
                data={
                    "action": "firmware_update",
                    "firmware_version": payload,
                },
            )
            self.assertEqual(res_waf.status_code, 200)
            html_waf = res_waf.get_data(as_text=True)
            self.assertNotIn("successfully deployed to sensors.", html_waf)
            self.assertIn(
                f"root@scada-system:~# {FLAG_WAF_BYPASS}",
                html_waf,
                f"Failed to return WAF bypass flag for payload: {payload}",
            )


if __name__ == "__main__":
    unittest.main()

