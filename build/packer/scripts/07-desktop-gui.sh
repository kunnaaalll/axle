#!/bin/bash
# ============================================================================
# AXLE OS — Desktop Environment Installation (Packer Stage 07)
# ============================================================================
# Installs a complete XFCE4 desktop environment branded as AXLE OS.
# Includes: Desktop, Login Screen, Boot Splash, GRUB Theme, Auto-start Dashboard
# ============================================================================
set -euo pipefail

echo "=== [Stage 07] Installing AXLE OS Desktop Environment ==="

export DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------------------
# 1. Install XFCE4 Desktop Environment (lightweight, fast)
# ---------------------------------------------------------------------------
echo "[07.1] Installing XFCE4 Desktop Environment..."
apt-get install -y --no-install-recommends \
    xfce4 \
    xfce4-terminal \
    xfce4-panel \
    xfce4-settings \
    xfce4-taskmanager \
    xfce4-notifyd \
    xfce4-screenshooter \
    thunar \
    mousepad \
    ristretto \
    xfce4-whiskermenu-plugin \
    network-manager-gnome \
    dbus-x11

# ---------------------------------------------------------------------------
# 2. Install Display Manager (LightDM) for Login Screen
# ---------------------------------------------------------------------------
echo "[07.2] Installing LightDM Display Manager..."
apt-get install -y --no-install-recommends \
    lightdm \
    lightdm-gtk-greeter \
    lightdm-gtk-greeter-settings

# Set LightDM as default display manager
echo "/usr/sbin/lightdm" > /etc/X11/default-display-manager
dpkg-reconfigure -f noninteractive lightdm

# ---------------------------------------------------------------------------
# 3. Install Plymouth Boot Splash
# ---------------------------------------------------------------------------
echo "[07.3] Installing Plymouth Boot Splash..."
apt-get install -y plymouth plymouth-themes

# ---------------------------------------------------------------------------
# 4. Install Additional Desktop Software
# ---------------------------------------------------------------------------
echo "[07.4] Installing Desktop Software..."
apt-get install -y --no-install-recommends \
    firefox \
    fonts-inter \
    fonts-noto \
    fonts-noto-color-emoji \
    papirus-icon-theme \
    arc-theme \
    xdg-utils \
    xdg-user-dirs \
    pulseaudio \
    pavucontrol \
    network-manager \
    nm-tray \
    gnome-keyring

# ---------------------------------------------------------------------------
# 5. Install VNC/RDP for Remote Desktop Access (critical for EC2)
# ---------------------------------------------------------------------------
echo "[07.5] Installing Remote Desktop Access..."
apt-get install -y \
    tigervnc-standalone-server \
    tigervnc-common \
    xrdp

# Configure xRDP to use XFCE
echo "xfce4-session" > /etc/skel/.xsession
systemctl enable xrdp

# ---------------------------------------------------------------------------
# 6. Apply AXLE OS Branding
# ---------------------------------------------------------------------------
echo "[07.6] Applying AXLE OS Desktop Branding..."

# Wallpapers
mkdir -p /usr/share/backgrounds/axle
cp /tmp/build/desktop/wallpapers/*.png /usr/share/backgrounds/axle/

# Plymouth boot splash
cp -r /tmp/build/desktop/plymouth/axle-os /usr/share/plymouth/themes/
plymouth-set-default-theme axle-os || true

# LightDM login screen
mkdir -p /usr/share/backgrounds/axle
cp /tmp/build/desktop/lightdm/background.png /usr/share/backgrounds/axle/login-bg.png
cp /tmp/build/desktop/lightdm/lightdm-gtk-greeter.conf /etc/lightdm/lightdm-gtk-greeter.conf

# GRUB bootloader theme
mkdir -p /boot/grub/themes/axle
cp /tmp/build/desktop/grub/theme.txt /boot/grub/themes/axle/
sed -i 's|#GRUB_THEME=.*|GRUB_THEME="/boot/grub/themes/axle/theme.txt"|' /etc/default/grub
update-grub || true

# XFCE4 default settings
mkdir -p /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/
cp /tmp/build/desktop/xfce4/*.xml /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/

# Desktop shortcuts
mkdir -p /etc/skel/Desktop
cp /tmp/build/desktop/autostart/*.desktop /etc/skel/Desktop/ 2>/dev/null || true
chmod +x /etc/skel/Desktop/*.desktop 2>/dev/null || true

# Auto-launch AXLE Dashboard on login
mkdir -p /etc/skel/.config/autostart
cp /tmp/build/desktop/autostart/axle-dashboard.desktop /etc/skel/.config/autostart/ 2>/dev/null || true

# ---------------------------------------------------------------------------
# 7. Configure Default User Experience
# ---------------------------------------------------------------------------
echo "[07.7] Configuring Default User Experience..."

# Set dark theme as default
mkdir -p /etc/skel/.config/gtk-3.0
cat > /etc/skel/.config/gtk-3.0/settings.ini << 'GTKEOF'
[Settings]
gtk-theme-name=Arc-Dark
gtk-icon-theme-name=Papirus-Dark
gtk-font-name=Inter 10
gtk-cursor-theme-name=Adwaita
gtk-application-prefer-dark-theme=1
GTKEOF

# Set XFCE terminal defaults
mkdir -p /etc/skel/.config/xfce4/terminal
cat > /etc/skel/.config/xfce4/terminal/terminalrc << 'TERMEOF'
[Configuration]
FontName=Monospace 11
ColorBackground=#0a0a2e
ColorForeground=#e2e8f0
ColorCursorForeground=#60a5fa
ColorCursorUseDefault=FALSE
MiscAlwaysShowTabs=FALSE
MiscBell=FALSE
MiscConfirmClose=FALSE
MiscDefaultGeometry=120x35
ScrollingLines=10000
TabActivityColor=#60a5fa
TERMEOF

echo "=== [Stage 07] Desktop Environment Installation Complete ==="
