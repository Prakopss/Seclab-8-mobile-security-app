import io
import os
import zipfile
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_file,
)

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY", "ios-smart-factory-gateway-scada-session-2026"
)

# Constants for authentication and simulation
GATEWAY_API_KEY = "IOS_FACTORY_SECRET_9912"
VALID_SCADA_USERNAME = "admin"
VALID_SCADA_PASSWORDS = {"password", "admin"}
FLAG_SECRET = "FLAG{IOT_SCADA_C0MPR0MISED_SUCCESS}"
FLAG_WAF_BYPASS = "FLAG{ELITE_WAF_BYPASS_ACHIEVED_2026}"

# Simulated decompiled Android files generated dynamically in memory
ANDROID_MANIFEST_XML = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="id.co.industrisejahtera.smartfactory.teknisi"
    android:versionCode="204"
    android:versionName="2.0.4-industrial">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:usesCleartextTraffic="true"
        android:theme="@style/Theme.SmartFactoryTeknisi">

        <activity
            android:name=".ui.SplashActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Activity for Plant Floor Technician Gateway Configuration -->
        <activity
            android:name=".provisioning.GatewayMaintenanceActivity"
            android:exported="true"
            android:label="Gateway Direct Provisioning" />

        <service
            android:name=".telemetry.ModbusSyncService"
            android:enabled="true"
            android:exported="false" />

    </application>
</manifest>
"""

STRINGS_XML = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">IOS Teknisi Mobile</string>
    <string name="company_name">PT Industri Otomasi Sejahtera</string>
    <string name="gateway_endpoint">https://gateway.industrisejahtera.co.id/api/v2</string>
    <string name="modbus_polling_interval">5000</string>
    <string name="gateway_api_key">IOS_FACTORY_SECRET_9912</string>
    <string name="plc_cluster_region">PLANT-CIKAMPEK-01</string>
    <string name="support_ext">Ext. 4410 - Pusat Kendali Otomasi</string>
</resources>
"""


def evaluate_firmware_update(version_input: str) -> dict:
    """
    Isolated simulation of the IoT Sensor Firmware Update process.
    Does NOT invoke os.system or subprocess. Evaluates input strings safely
    in Python to simulate OS command execution behavior on an embedded gateway.
    """
    cleaned = version_input.strip()
    if not cleaned:
        return {
            "status": "error",
            "message": "Input Firmware Version tidak boleh kosong.",
            "terminal_output": None,
        }

    lower_input = cleaned.lower()

    # Check for Linux Command Obfuscation (WAF Evasion) patterns when literal "cat" is absent
    obfuscated_cat_patterns = (
        "c''at",
        "c\\at",
        'c""at',
        "/bin/?at",
    )
    if "cat" not in lower_input and any(
        pattern in lower_input for pattern in obfuscated_cat_patterns
    ):
        simulated_lines = [
            f"$ /usr/sbin/fw-updater --deploy --version {cleaned}",
            "[INFO] Initializing OTA broadcast to Modbus-RTU sensor array...",
            "[OK] Package checksum verified.",
            f"root@scada-system:~# {FLAG_WAF_BYPASS}",
        ]
        return {
            "status": "compromised",
            "message": f"root@scada-system:~# {FLAG_WAF_BYPASS}",
            "terminal_output": "\n".join(simulated_lines),
        }

    # Check for shell command separator characters (; | &&)
    has_injection_operator = (
        ";" in cleaned or "|" in cleaned or "&&" in cleaned
    )

    # Check for target inspection commands (whoami, ls, cat)
    has_target_command = any(
        cmd in lower_input for cmd in ("whoami", "ls", "cat")
    )

    if has_injection_operator and has_target_command:
        simulated_lines = [
            f"$ /usr/sbin/fw-updater --deploy --version {cleaned}",
            "[INFO] Initializing OTA broadcast to Modbus-RTU sensor array...",
            "[OK] Package checksum verified.",
        ]

        if "whoami" in lower_input:
            simulated_lines.append("root")
        if "ls" in lower_input:
            simulated_lines.append(
                "fw-updater.sh  modbus_map.conf  plc_override.key  sensor_nodes.db  flag.txt"
            )
        if "cat" in lower_input:
            simulated_lines.append(
                "# SCADA Master Node Secret Configuration\n"
                "NODE_ID=SCADA-PRIMARY-01\n"
                f"MASTER_TOKEN={FLAG_SECRET}"
            )

        simulated_lines.append(f"root@scada-system:~# {FLAG_SECRET}")

        return {
            "status": "compromised",
            "message": f"root@scada-system:~# {FLAG_SECRET}",
            "terminal_output": "\n".join(simulated_lines),
        }

    # Normal firmware deployment response
    return {
        "status": "success",
        "message": f"Firmware {cleaned} successfully deployed to sensors.",
        "terminal_output": None,
    }


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/download/mobile-app", methods=["GET"])
def download_mobile_app():
    """
    Dynamically generates an in-memory ZIP file containing AndroidManifest.xml
    and strings.xml using io.BytesIO and zipfile.
    """
    memory_file = io.BytesIO()
    with zipfile.ZipFile(
        memory_file, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        zf.writestr("AndroidManifest.xml", ANDROID_MANIFEST_XML.strip() + "\n")
        zf.writestr("strings.xml", STRINGS_XML.strip() + "\n")

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype="application/zip",
        as_attachment=True,
        download_name="ios_teknisi_mobile_android_src.zip",
    )


@app.route("/gateway-login", methods=["GET", "POST"])
def gateway_login():
    error_message = None

    if request.method == "POST":
        submitted_key = request.form.get("gateway_api_key", "").strip()
        if submitted_key == GATEWAY_API_KEY:
            session["gateway_authenticated"] = True
            return redirect(url_for("scada_panel"))
        else:
            error_message = (
                "Otorisasi Ditolak: Gateway API Key tidak valid atau tidak "
                "terdaftar pada klaster pengendali utama."
            )

    return render_template("gateway_login.html", error_message=error_message)


@app.route("/scada-panel", methods=["GET", "POST"])
def scada_panel():
    # Require Gateway API Key authorization first
    if not session.get("gateway_authenticated"):
        return redirect(url_for("gateway_login"))

    scada_authenticated = session.get("scada_authenticated", False)
    override_error = None
    firmware_result = None
    firmware_version_input = ""

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "scada_override" or not scada_authenticated:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            if (
                username == VALID_SCADA_USERNAME
                and password in VALID_SCADA_PASSWORDS
            ):
                session["scada_authenticated"] = True
                scada_authenticated = True
            else:
                override_error = (
                    "Kredensial SCADA Override tidak valid. Akses ke panel "
                    "kontrol PLC dan aktuator ditolak."
                )

        elif action == "firmware_update" and scada_authenticated:
            firmware_version_input = request.form.get(
                "firmware_version", ""
            ).strip()
            firmware_result = evaluate_firmware_update(firmware_version_input)

    # Simulated industrial telemetry data for SCADA dashboard
    telemetry = {
        "machine_temp": "78.4 °C",
        "machine_temp_status": "NORMAL (Batas Aman: 95.0 °C)",
        "water_pressure": "4.85 Bar",
        "water_pressure_status": "STABIL (Rentang: 4.20 - 5.50 Bar)",
        "turbine_rpm": "3,600 RPM",
        "active_sensors": "48 / 48 Node Online",
        "plc_controller": "SIMATIC-S7-1500 (Master Node #01)",
        "current_firmware": "v2.0.8-stable",
    }

    return render_template(
        "scada_panel.html",
        scada_authenticated=scada_authenticated,
        override_error=override_error,
        firmware_result=firmware_result,
        firmware_version_input=firmware_version_input,
        telemetry=telemetry,
    )


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
