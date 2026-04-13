#!/bin/bash
# ============================================================================
# AXLE OS — Premium UX & Terminal Overhaul (Stage 08)
# ============================================================================
set -euo pipefail

echo "=== [Stage 08] Applying Premium UX & Terminal Overhaul ==="

export DEBIAN_FRONTEND=noninteractive

# 1. Install plank (macOS-like dock), zsh, and theme dependencies
apt-get install -y plank zsh git curl gtk2-engines-murrine gtk2-engines-pixbuf sassc optipng libglib2.0-dev-bin unzip

# 2. Change default shell to zsh for all users
chsh -s $(which zsh) ubuntu || true
chsh -s $(which zsh) root || true

# 3. Setup Oh-My-Zsh & Powerlevel10k for ubuntu user
sudo -u ubuntu bash -c '
    # Install Oh-My-Zsh
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    
    # Install Powerlevel10k
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/.oh-my-zsh/custom/themes/powerlevel10k
    
    # Install Plugins
    git clone https://github.com/zsh-users/zsh-autosuggestions ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting

    # Configure .zshrc
    sed -i '\''s/ZSH_THEME="robbyrussell"/ZSH_THEME="powerlevel10k\/powerlevel10k"/g'\'' ~/.zshrc
    sed -i '\''s/plugins=(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/g'\'' ~/.zshrc
    
    # Disable p10k config wizard
    echo "POWERLEVEL9K_DISABLE_CONFIGURATION_WIZARD=true" >> ~/.zshrc
'

# 4. Install premium Orchis GTK theme (Rounded, Dark, Glassy)
cd /tmp
git clone https://github.com/vinceliuice/Orchis-theme.git
cd Orchis-theme
./install.sh -t default -c dark -s compact
cd /tmp
rm -rf Orchis-theme

# 5. XFCE Config tweaks (Applied to default skel for new users)
mkdir -p /etc/skel/.config/xfce4/terminal
cat > /etc/skel/.config/xfce4/terminal/terminalrc << 'TERMEOF'
[Configuration]
FontName=MesloLGS NF 12
ColorBackground=#000511
ColorForeground=#dcdfe4
ColorCursorForeground=#60a5fa
ColorCursorUseDefault=FALSE
MiscAlwaysShowTabs=FALSE
MiscBell=FALSE
MiscConfirmClose=FALSE
MiscDefaultGeometry=120x35
ScrollingLines=100000
TabActivityColor=#60a5fa
BackgroundDarkness=0.90
BackgroundMode=TERMINAL_BACKGROUND_TRANSPARENT
TERMEOF

echo "=== [Stage 08] Overhaul Complete ==="
