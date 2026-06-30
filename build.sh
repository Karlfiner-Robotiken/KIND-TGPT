#!/bin/bash
# Termux package build script for KIND-TGPT
# Maintainer: Karlfiner-Robotiken

TERMUX_PKG_HOMEPAGE="https://github.com/Karlfiner-Robotiken/KIND-TGPT"
TERMUX_PKG_DESCRIPTION="Advanced AI System with TGPT Integration and Self-Learning"
TERMUX_PKG_LICENSE="MIT"
TERMUX_PKG_MAINTAINER="Karlfiner-Robotiken"
TERMUX_PKG_VERSION="4.0.0"
TERMUX_PKG_SRCURL="https://github.com/Karlfiner-Robotiken/KIND-TGPT/archive/v${TERMUX_PKG_VERSION}.tar.gz"
TERMUX_PKG_SHA256="skip-for-local-build"
TERMUX_PKG_DEPENDS="python, nodejs, git"
TERMUX_PKG_PLATFORM_INDEPENDENT=true
TERMUX_PKG_BUILD_IN_SRC=true

termux_step_make_install() {
    # Install Python dependencies
    pip install flask flask-cors
    
    # Install TGPT globally
    npm install -g tgpt
    
    # Create installation directory
    mkdir -p $TERMUX_PREFIX/share/kind-tgpt
    cp -r src $TERMUX_PREFIX/share/kind-tgpt/
    cp -r scripts $TERMUX_PREFIX/share/kind-tgpt/
    cp -r config $TERMUX_PREFIX/share/kind-tgpt/
    
    # Create bin executable
    cat > $TERMUX_PREFIX/bin/kind-tgpt << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
KIND_DIR="$PREFIX/share/kind-tgpt"

case "$1" in
    start)
        cd $KIND_DIR
        python3 src/kind_tgpt.py &
        sleep 2
        echo -e "\033[0;32m✅ KIND-TGPT started on http://localhost:5000\033[0m"
        echo -e "\033[0;34m🌐 Open: http://localhost:5000\033[0m"
        ;;
    stop)
        pkill -f "kind_tgpt.py"
        echo -e "\033[0;32m✅ KIND-TGPT stopped\033[0m"
        ;;
    restart)
        pkill -f "kind_tgpt.py"
        sleep 1
        cd $KIND_DIR
        python3 src/kind_tgpt.py &
        sleep 2
        echo -e "\033[0;32m✅ KIND-TGPT restarted\033[0m"
        ;;
    status)
        if curl -s http://localhost:5000/health > /dev/null 2>&1; then
            echo -e "\033[0;32m✅ KIND-TGPT is running\033[0m"
            curl -s http://localhost:5000/api/stats | python3 -m json.tool
        else
            echo -e "\033[0;31m❌ KIND-TGPT is stopped\033[0m"
        fi
        ;;
    stats)
        curl -s http://localhost:5000/api/stats | python3 -m json.tool
        ;;
    cli)
        cd $KIND_DIR
        python3 -c "
from src.kind_tgpt import kind
import sys

print('\033[1;36m' + '='*60 + '\033[0m')
print('\033[1;35m🧠 KIND-TGPT CLI Mode - Karlfiner-Robotiken\033[0m')
print('\033[1;36m' + '='*60 + '\033[0m')
print('\033[0;33mType your questions or \"exit\" to quit\033[0m\n')

while True:
    try:
        prob = input('\033[1;32m💬 You: \033[0m')
        if prob.lower() in ['exit', 'quit', 'q']:
            print('\n\033[1;35m👋 Goodbye! Have a great day!\033[0m')
            break
        if prob.strip():
            print('\n\033[1;34m🤖 KIND-TGPT:\033[0m')
            print('\033[0;36m' + kind.solve(prob, source=\"cli\") + '\033[0m')
            print('\033[1;30m' + '-'*60 + '\033[0m')
    except KeyboardInterrupt:
        print('\n\n\033[1;35m👋 Goodbye!\033[0m')
        break
    except Exception as e:
        print(f'\033[0;31m❌ Error: {e}\033[0m')
"
        ;;
    memory)
        echo -e "\033[0;34m📚 Memory Statistics:\033[0m"
        cat ~/.kind_tgpt/memory.json 2>/dev/null | python3 -m json.tool || echo "No memory data yet"
        ;;
    clear)
        rm -f ~/.kind_tgpt/memory.json ~/.kind_tgpt/history.log ~/.kind_tgpt/learnings.json
        echo -e "\033[0;32m✅ Memory cleared successfully\033[0m"
        ;;
    install-tgpt)
        echo -e "\033[0;33m📦 Installing TGPT...\033[0m"
        npm install -g tgpt
        echo -e "\033[0;32m✅ TGPT installed!\033[0m"
        ;;
    update)
        echo -e "\033[0;33m🔄 Updating KIND-TGPT...\033[0m"
        cd $KIND_DIR
        git pull origin main
        echo -e "\033[0;32m✅ Update complete!\033[0m"
        ;;
    version)
        echo -e "\033[0;36mKIND-TGPT v4.0.0 GODMODE\033[0m"
        echo -e "\033[0;33mMaintainer: Karlfiner-Robotiken\033[0m"
        echo -e "\033[0;33mLicense: MIT\033[0m"
        ;;
    help|--help|-h)
        echo -e "\033[1;36m╔══════════════════════════════════════════════════════════════╗\033[0m"
        echo -e "\033[1;36m║           🤖 KIND-TGPT - Command Reference                      ║\033[0m"
        echo -e "\033[1;36m╚══════════════════════════════════════════════════════════════╝\033[0m"
        echo ""
        echo -e "\033[1;33m📱 Commands:\033[0m"
        echo -e "  \033[1;32mstart\033[0m         - Start web server on port 5000"
        echo -e "  \033[1;32mstop\033[0m          - Stop web server"
        echo -e "  \033[1;32mrestart\033[0m       - Restart web server"
        echo -e "  \033[1;32mstatus\033[0m        - Check server status and stats"
        echo -e "  \033[1;32mstats\033[0m         - Show detailed statistics"
        echo -e "  \033[1;32mcli\033[0m           - Interactive CLI mode"
        echo -e "  \033[1;32mmemory\033[0m        - View memory contents"
        echo -e "  \033[1;32mclear\033[0m         - Clear all memory data"
        echo -e "  \033[1;32minstall-tgpt\033[0m  - Install/update TGPT engine"
        echo -e "  \033[1;32mupdate\033[0m        - Update KIND-TGPT to latest"
        echo -e "  \033[1;32mversion\033[0m       - Show version information"
        echo -e "  \033[1;32mhelp\033[0m          - Show this help"
        echo ""
        echo -e "\033[1;33m🌐 Web Interface:\033[0m"
        echo -e "  http://localhost:5000 - Main dashboard"
        echo -e "  http://localhost:5000/api - REST API"
        echo ""
        echo -e "\033[1;33m📝 Examples:\033[0m"
        echo -e "  kind-tgpt start     # Start the AI server"
        echo -e "  kind-tgpt cli       # Chat in terminal"
        echo -e "  kind-tgpt status    # Check if running"
        ;;
    *)
        if [ -z "$1" ]; then
            echo -e "\033[1;35m🤖 KIND-TGPT v4.0.0 - Karlfiner-Robotiken\033[0m"
            echo -e "\033[0;33mRun 'kind-tgpt help' for commands\033[0m"
        else
            echo -e "\033[0;31m❌ Unknown command: $1\033[0m"
            echo -e "\033[0;33mRun 'kind-tgpt help' for available commands\033[0m"
        fi
        ;;
esac
EOF
    
    chmod +x $TERMUX_PREFIX/bin/kind-tgpt
    
    # Create desktop entry for graphical environments
    mkdir -p $TERMUX_PREFIX/share/applications
    cat > $TERMUX_PREFIX/share/applications/kind-tgpt.desktop << 'EOF'
[Desktop Entry]
Name=KIND-TGPT
Comment=Advanced AI System
Exec=kind-tgpt start
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=Development;AI;
EOF
    
    # Create bash completion
    mkdir -p $TERMUX_PREFIX/share/bash-completion/completions
    cat > $TERMUX_PREFIX/share/bash-completion/completions/kind-tgpt << 'EOF'
_kind_tgpt_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="start stop restart status stats cli memory clear install-tgpt update version help"
    
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}
complete -F _kind_tgpt_completion kind-tgpt
EOF
    
    echo -e "\033[0;32m✅ KIND-TGPT has been installed successfully!\033[0m"
    echo -e "\033[0;34m📱 Run 'kind-tgpt start' to begin\033[0m"
}

termux_step_create_debscripts() {
    cat <<- POSTINST > ./postinst
    #!/bin/bash
    echo -e "\033[0;34m🤖 Setting up KIND-TGPT...\033[0m"
    mkdir -p ~/.kind_tgpt
    echo -e "\033[0;32m✅ Setup complete!\033[0m"
    echo -e "\033[0;33mRun 'kind-tgpt help' to get started\033[0m"
POSTINST
}
