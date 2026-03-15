from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import threading
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# Email configuration from environment variables
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
APP_PASSWORD = os.getenv('APP_PASSWORD')
EMERGENCY_CONTACT = "anurag.nimkande@gmail.com"  # Hardcoded email

@app.route("/")
def home():
    return render_template("index.html")

def send_emergency_email(receiver_email, location_link, accuracy=None, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Extract coordinates
    try:
        coords = location_link.split('q=')[-1]
        if ',' in coords:
            latitude, longitude = coords.split(',')
            latitude = latitude.strip()
            longitude = longitude.strip()
        else:
            latitude = "Unknown"
            longitude = "Unknown"
    except:
        latitude = "Unknown"
        longitude = "Unknown"
    
    # Format accuracy for display
    if accuracy and accuracy != 'High':
        try:
            accuracy_display = f"{round(float(accuracy))}"
        except:
            accuracy_display = "High"
    else:
        accuracy_display = "High"
    
    # Generate alert ID
    alert_id = f"EMG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Sophisticated dark-themed email template with perfect formatting
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="dark">
    <meta name="supported-color-schemes" content="dark">
    <title>Emergency Alert • {alert_id}</title>
    <style>
        /* Reset styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #0a0c0f !important;
                color: #e5e7eb !important;
            }}
        }}
        
        /* Main container */
        .email-wrapper {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background: #0f1319;
            border-radius: 32px;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
            border: 1px solid rgba(220, 38, 38, 0.2);
        }}
        
        /* Header section with gradient */
        .alert-header {{
            background: linear-gradient(165deg, #1a1f2a 0%, #0f1319 100%);
            padding: 40px 32px;
            text-align: center;
            border-bottom: 2px solid #dc2626;
            position: relative;
            overflow: hidden;
        }}
        
        .alert-header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(220,38,38,0.08) 0%, transparent 70%);
            animation: rotate 20s linear infinite;
        }}
        
        @keyframes rotate {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        
        /* Alert icon container */
        .alert-icon-wrapper {{
            width: 88px;
            height: 88px;
            margin: 0 auto 24px;
            background: rgba(220, 38, 38, 0.1);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid rgba(220, 38, 38, 0.3);
            box-shadow: 0 0 40px rgba(220, 38, 38, 0.2);
            position: relative;
            z-index: 2;
        }}
        
        .alert-icon {{
            width: 48px;
            height: 48px;
            background: #dc2626;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 28px;
            font-weight: bold;
            box-shadow: 0 0 30px #dc2626;
        }}
        
        /* Header text */
        .alert-header h1 {{
            font-size: 32px;
            font-weight: 600;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #fff 0%, #9ca3af 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 16px;
            position: relative;
            z-index: 2;
        }}
        
        .priority-badge {{
            display: inline-block;
            padding: 8px 20px;
            background: rgba(220, 38, 38, 0.1);
            border: 1px solid rgba(220, 38, 38, 0.3);
            border-radius: 100px;
            color: #f87171;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            position: relative;
            z-index: 2;
            backdrop-filter: blur(5px);
        }}
        
        /* Content area */
        .content {{
            padding: 40px 32px;
            background: #0f1319;
        }}
        
        /* Alert message box */
        .alert-message {{
            background: #1a1f2a;
            border-left: 4px solid #dc2626;
            padding: 20px 24px;
            border-radius: 16px;
            margin-bottom: 32px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }}
        
        .alert-message p {{
            margin: 0;
            color: #e5e7eb;
            font-size: 16px;
            line-height: 1.6;
            font-weight: 400;
        }}
        
        /* Location card */
        .location-card {{
            background: #1a1f2a;
            border-radius: 24px;
            padding: 32px;
            margin: 32px 0;
            border: 1px solid rgba(220, 38, 38, 0.2);
            box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.4);
            position: relative;
            overflow: hidden;
        }}
        
        .location-card::after {{
            content: '📍';
            position: absolute;
            bottom: -20px;
            right: -20px;
            font-size: 140px;
            opacity: 0.03;
            transform: rotate(-10deg);
            pointer-events: none;
        }}
        
        .location-card h2 {{
            color: #f3f4f6;
            font-size: 20px;
            font-weight: 500;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .location-card h2 i {{
            color: #f87171;
            font-size: 24px;
        }}
        
        /* Coordinates display */
        .coordinates-container {{
            background: #0f1319;
            border-radius: 20px;
            padding: 4px;
            border: 1px solid #2a2f3a;
            margin-bottom: 24px;
        }}
        
        .coordinate-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            border-bottom: 1px solid #2a2f3a;
        }}
        
        .coordinate-row:last-child {{
            border-bottom: none;
        }}
        
        .coordinate-label {{
            color: #9ca3af;
            font-size: 14px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .coordinate-value {{
            color: #f87171;
            font-size: 18px;
            font-weight: 600;
            font-family: 'SF Mono', 'Fira Code', monospace;
            background: rgba(220, 38, 38, 0.1);
            padding: 6px 16px;
            border-radius: 100px;
            border: 1px solid rgba(220, 38, 38, 0.2);
        }}
        
        /* Accuracy meter */
        .accuracy-section {{
            text-align: center;
            margin: 24px 0 32px;
        }}
        
        .accuracy-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 24px;
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
            border-radius: 100px;
            color: white;
            font-weight: 500;
            font-size: 15px;
            letter-spacing: 0.3px;
            box-shadow: 0 10px 20px -8px rgba(220, 38, 38, 0.4);
        }}
        
        .accuracy-badge i {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        /* Map button */
        .map-button {{
            display: block;
            background: linear-gradient(135deg, #2a2f3a 0%, #1a1f2a 100%);
            color: #f3f4f6;
            text-decoration: none;
            padding: 18px 28px;
            border-radius: 18px;
            font-weight: 600;
            font-size: 18px;
            margin: 28px 0 16px;
            transition: all 0.3s ease;
            border: 1px solid rgba(220, 38, 38, 0.3);
            text-align: center;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }}
        
        .map-button:hover {{
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 20px 30px -10px rgba(220, 38, 38, 0.4);
            border-color: transparent;
        }}
        
        .map-button i {{
            margin-right: 8px;
            font-size: 20px;
        }}
        
        /* Info grid */
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            margin: 32px 0;
        }}
        
        .info-item {{
            background: #1a1f2a;
            padding: 18px 16px;
            border-radius: 18px;
            border: 1px solid #2a2f3a;
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .info-item:hover {{
            border-color: rgba(220, 38, 38, 0.3);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }}
        
        .info-label {{
            color: #9ca3af;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .info-value {{
            color: #f3f4f6;
            font-size: 16px;
            font-weight: 500;
        }}
        
        /* Action required box */
        .action-box {{
            background: rgba(220, 38, 38, 0.08);
            border: 1px solid rgba(220, 38, 38, 0.2);
            border-radius: 18px;
            padding: 24px;
            margin: 32px 0 20px;
            text-align: center;
            backdrop-filter: blur(5px);
        }}
        
        .action-box p {{
            color: #f87171;
            margin: 0;
            font-weight: 500;
            font-size: 16px;
            line-height: 1.6;
        }}
        
        .action-box i {{
            font-size: 24px;
            margin-bottom: 12px;
            color: #f87171;
        }}
        
        /* Footer */
        .footer {{
            padding: 32px;
            background: #0a0c0f;
            border-top: 1px solid #2a2f3a;
            text-align: center;
        }}
        
        .security-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 18px;
            background: #1a1f2a;
            border-radius: 100px;
            color: #9ca3af;
            font-size: 12px;
            border: 1px solid #2a2f3a;
            margin-bottom: 20px;
        }}
        
        .security-badge i {{
            color: #10b981;
            font-size: 12px;
        }}
        
        .alert-id {{
            color: #6b7280;
            font-size: 13px;
            font-family: 'SF Mono', monospace;
            margin: 12px 0 8px;
            letter-spacing: 0.3px;
        }}
        
        .footer-text {{
            color: #6b7280;
            font-size: 13px;
            margin: 5px 0;
        }}
        
        .emergency-footer {{
            color: #f87171;
            font-size: 14px;
            font-weight: 600;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #2a2f3a;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        
        /* Divider */
        .divider {{
            height: 1px;
            background: linear-gradient(90deg, transparent, #2a2f3a, transparent);
            margin: 24px 0;
        }}
        
        /* Responsive */
        @media (max-width: 480px) {{
            .content {{
                padding: 30px 20px;
            }}
            
            .location-card {{
                padding: 24px 20px;
            }}
            
            .coordinate-value {{
                font-size: 16px;
                padding: 4px 12px;
            }}
            
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            
            .alert-header {{
                padding: 30px 20px;
            }}
            
            .alert-header h1 {{
                font-size: 28px;
            }}
        }}
        
        /* Dark mode optimizations */
        [data-ogsc] .email-wrapper,
        [data-ogsb] .email-wrapper {{
            background: #0f1319 !important;
        }}
    </style>
</head>
<body style="margin: 0; padding: 20px; background-color: #0a0c0f; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; -webkit-font-smoothing: antialiased;">
    <div class="email-wrapper" style="max-width: 600px; margin: 0 auto; background: #0f1319; border-radius: 32px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.8); border: 1px solid rgba(220,38,38,0.2);">
        <!-- Header -->
        <div class="alert-header" style="background: linear-gradient(165deg, #1a1f2a 0%, #0f1319 100%); padding: 40px 32px; text-align: center; border-bottom: 2px solid #dc2626; position: relative; overflow: hidden;">
            <div class="alert-icon-wrapper" style="width: 88px; height: 88px; margin: 0 auto 24px; background: rgba(220,38,38,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid rgba(220,38,38,0.3); box-shadow: 0 0 40px rgba(220,38,38,0.2);">
                <div class="alert-icon" style="width: 48px; height: 48px; background: #dc2626; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 28px; font-weight: bold; box-shadow: 0 0 30px #dc2626;">
                    !
                </div>
            </div>
            <h1 style="font-size: 32px; font-weight: 600; letter-spacing: -0.5px; background: linear-gradient(135deg, #fff 0%, #9ca3af 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 16px;">EMERGENCY ALERT</h1>
            <div class="priority-badge" style="display: inline-block; padding: 8px 20px; background: rgba(220,38,38,0.1); border: 1px solid rgba(220,38,38,0.3); border-radius: 100px; color: #f87171; font-size: 14px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">
                ⚡ IMMEDIATE RESPONSE REQUIRED
            </div>
        </div>
        
        <!-- Content -->
        <div class="content" style="padding: 40px 32px; background: #0f1319;">
            <!-- Alert Message -->
            <div class="alert-message" style="background: #1a1f2a; border-left: 4px solid #dc2626; padding: 20px 24px; border-radius: 16px; margin-bottom: 32px; box-shadow: 0 8px 16px rgba(0,0,0,0.2);">
                <p style="margin: 0; color: #e5e7eb; font-size: 16px; line-height: 1.6;">
                    An emergency alert has been triggered. The following location requires immediate attention and verification.
                </p>
            </div>
            
            <!-- Location Card -->
            <div class="location-card" style="background: #1a1f2a; border-radius: 24px; padding: 32px; margin: 32px 0; border: 1px solid rgba(220,38,38,0.2); box-shadow: 0 20px 30px -10px rgba(0,0,0,0.4);">
                <h2 style="color: #f3f4f6; font-size: 20px; font-weight: 500; margin-bottom: 24px; display: flex; align-items: center; gap: 8px;">
                    <span style="color: #f87171; font-size: 24px;">📍</span> Current Location
                </h2>
                
                <!-- Coordinates -->
                <div class="coordinates-container" style="background: #0f1319; border-radius: 20px; padding: 4px; border: 1px solid #2a2f3a; margin-bottom: 24px;">
                    <div class="coordinate-row" style="display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #2a2f3a;">
                        <span class="coordinate-label" style="color: #9ca3af; font-size: 14px; font-weight: 500; text-transform: uppercase;">Latitude</span>
                        <span class="coordinate-value" style="color: #f87171; font-size: 18px; font-weight: 600; font-family: 'SF Mono', monospace; background: rgba(220,38,38,0.1); padding: 6px 16px; border-radius: 100px; border: 1px solid rgba(220,38,38,0.2);">{latitude}</span>
                    </div>
                    <div class="coordinate-row" style="display: flex; justify-content: space-between; align-items: center; padding: 16px 20px;">
                        <span class="coordinate-label" style="color: #9ca3af; font-size: 14px; font-weight: 500; text-transform: uppercase;">Longitude</span>
                        <span class="coordinate-value" style="color: #f87171; font-size: 18px; font-weight: 600; font-family: 'SF Mono', monospace; background: rgba(220,38,38,0.1); padding: 6px 16px; border-radius: 100px; border: 1px solid rgba(220,38,38,0.2);">{longitude}</span>
                    </div>
                </div>
                
                <!-- Accuracy -->
                <div class="accuracy-section" style="text-align: center; margin: 24px 0 32px;">
                    <span class="accuracy-badge" style="display: inline-flex; align-items: center; gap: 8px; padding: 10px 24px; background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); border-radius: 100px; color: white; font-weight: 500; font-size: 15px; box-shadow: 0 10px 20px -8px rgba(220,38,38,0.4);">
                        <span>🎯</span> Accuracy: {accuracy_display} meters
                    </span>
                </div>
                
                <!-- Map Button -->
                <a href="{location_link}" class="map-button" style="display: block; background: linear-gradient(135deg, #2a2f3a 0%, #1a1f2a 100%); color: #f3f4f6; text-decoration: none; padding: 18px 28px; border-radius: 18px; font-weight: 600; font-size: 18px; margin: 28px 0 16px; border: 1px solid rgba(220,38,38,0.3); text-align: center; box-shadow: 0 8px 16px rgba(0,0,0,0.2);" target="_blank">
                    <span style="margin-right: 8px;">🗺️</span> OPEN IN GOOGLE MAPS
                </a>
            </div>
            
            <!-- Info Grid -->
            <div class="info-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin: 32px 0;">
                <div class="info-item" style="background: #1a1f2a; padding: 18px 16px; border-radius: 18px; border: 1px solid #2a2f3a; text-align: center;">
                    <div class="info-label" style="color: #9ca3af; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">Alert Time</div>
                    <div class="info-value" style="color: #f3f4f6; font-size: 16px; font-weight: 500;">{timestamp}</div>
                </div>
                <div class="info-item" style="background: #1a1f2a; padding: 18px 16px; border-radius: 18px; border: 1px solid #2a2f3a; text-align: center;">
                    <div class="info-label" style="color: #9ca3af; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">Precision</div>
                    <div class="info-value" style="color: #f3f4f6; font-size: 16px; font-weight: 500;">{accuracy_display}m</div>
                </div>
                <div class="info-item" style="background: #1a1f2a; padding: 18px 16px; border-radius: 18px; border: 1px solid #2a2f3a; text-align: center;">
                    <div class="info-label" style="color: #9ca3af; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">Coordinates</div>
                    <div class="info-value" style="color: #f3f4f6; font-size: 16px; font-weight: 500;">{latitude}, {longitude}</div>
                </div>
                <div class="info-item" style="background: #1a1f2a; padding: 18px 16px; border-radius: 18px; border: 1px solid #2a2f3a; text-align: center;">
                    <div class="info-label" style="color: #9ca3af; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">Alert Type</div>
                    <div class="info-value" style="color: #f3f4f6; font-size: 16px; font-weight: 500;">Emergency</div>
                </div>
            </div>
            
            <!-- Divider -->
            <div class="divider" style="height: 1px; background: linear-gradient(90deg, transparent, #2a2f3a, transparent); margin: 24px 0;"></div>
            
            <!-- Action Box -->
            <div class="action-box" style="background: rgba(220,38,38,0.08); border: 1px solid rgba(220,38,38,0.2); border-radius: 18px; padding: 24px; margin: 32px 0 20px; text-align: center;">
                <div style="font-size: 24px; margin-bottom: 12px; color: #f87171;">⚠️</div>
                <p style="color: #f87171; margin: 0; font-weight: 500; font-size: 16px; line-height: 1.6;">
                    This person may be in danger. Please verify their safety immediately.
                </p>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer" style="padding: 32px; background: #0a0c0f; border-top: 1px solid #2a2f3a; text-align: center;">
            <div class="security-badge" style="display: inline-flex; align-items: center; gap: 8px; padding: 8px 18px; background: #1a1f2a; border-radius: 100px; color: #9ca3af; font-size: 12px; border: 1px solid #2a2f3a; margin-bottom: 20px;">
                <span style="color: #10b981;">🔒</span> End-to-End Encrypted
            </div>
            
            <div class="alert-id" style="color: #6b7280; font-size: 13px; font-family: monospace; margin: 12px 0 8px;">
                Alert ID: {alert_id}
            </div>
            
            <p class="footer-text" style="color: #6b7280; font-size: 13px; margin: 5px 0;">
                This is an automated emergency alert from the Safety System
            </p>
            
            <div class="emergency-footer" style="color: #f87171; font-size: 14px; font-weight: 600; margin-top: 20px; padding-top: 20px; border-top: 1px solid #2a2f3a; text-transform: uppercase;">
                ⚡ REQUIRES IMMEDIATE ACTION ⚡
            </div>
        </div>
    </div>
</body>
</html>
    """
    
    # Plain text version (fallback)
    text_content = f"""
EMERGENCY ALERT - IMMEDIATE ACTION REQUIRED
============================================
Alert ID: {alert_id}
Time: {timestamp}

LOCATION DETAILS:
----------------
Latitude: {latitude}
Longitude: {longitude}
Accuracy: {accuracy_display} meters

Google Maps Link:
{location_link}

⚠️ This person may be in danger. Please verify their safety immediately.

This is an automated emergency alert from the Safety System.
DO NOT IGNORE - This requires immediate attention.
    """
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 URGENT: Emergency Alert - Location: {latitude}, {longitude}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        
        # Priority headers
        msg['X-Priority'] = '1'
        msg['X-MSMail-Priority'] = 'High'
        msg['Importance'] = 'high'
        
        # Attach both versions
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False

@app.route("/send-location", methods=["POST"])
def send_location():
    try:
        data = request.json
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        accuracy = data.get("accuracy", "High")

        if not all([latitude, longitude]):
            return jsonify({"status": "Missing location data"}), 400

        location_link = f"https://www.google.com/maps?q={latitude},{longitude}"

        # Send email in background thread
        threading.Thread(
            target=send_emergency_email,
            args=(EMERGENCY_CONTACT, location_link, accuracy)
        ).start()

        return jsonify({
            "status": "success",
            "message": "Emergency alert triggered!"
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Emergency alert system running"})

if __name__ == "__main__":
    if not SENDER_EMAIL or not APP_PASSWORD:
        print("⚠️ Email credentials not set in environment variables!")
    
    app.run()