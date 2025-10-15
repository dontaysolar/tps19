#!/bin/bash
# TPS19 Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_banner() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════╗"
    echo "║         TPS19 Trading System         ║"
    echo "║      Crypto Trading Platform         ║"
    echo "╚══════════════════════════════════════╝"
    echo -e "${NC}"
}

check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Warning: .env file not found${NC}"
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${RED}Please edit .env with your configuration before proceeding${NC}"
        exit 1
    fi
}

setup() {
    echo -e "${GREEN}Setting up TPS19...${NC}"
    
    # Check Python version
    python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
        echo -e "${RED}Error: Python 3.8+ is required${NC}"
        exit 1
    fi
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    
    # Check environment
    check_env
    
    # Initialize database
    echo "Initializing database..."
    python main.py migrate
    
    echo -e "${GREEN}Setup complete!${NC}"
}

start() {
    check_env
    source venv/bin/activate
    
    if [ "$1" == "--live" ]; then
        echo -e "${RED}⚠️  WARNING: Starting in LIVE TRADING mode!${NC}"
        echo -e "${RED}This will execute real trades with real money.${NC}"
        read -p "Are you absolutely sure? Type 'YES' to continue: " confirm
        
        if [ "$confirm" != "YES" ]; then
            echo "Cancelled."
            exit 0
        fi
        
        python main.py start --live
    else
        echo -e "${GREEN}Starting in simulation mode...${NC}"
        python main.py start
    fi
}

stop() {
    echo -e "${YELLOW}Stopping TPS19...${NC}"
    
    # Find and kill the process
    if pgrep -f "python main.py" > /dev/null; then
        pkill -f "python main.py"
        echo -e "${GREEN}TPS19 stopped${NC}"
    else
        echo "TPS19 is not running"
    fi
}

status() {
    if pgrep -f "python main.py" > /dev/null; then
        echo -e "${GREEN}TPS19 is running${NC}"
        
        # Show process info
        ps aux | grep "python main.py" | grep -v grep
    else
        echo -e "${RED}TPS19 is not running${NC}"
    fi
}

test() {
    check_env
    source venv/bin/activate
    
    echo -e "${GREEN}Running tests...${NC}"
    python main.py test
}

logs() {
    if [ -f "logs/tps19.log" ]; then
        tail -f logs/tps19.log
    else
        echo "No log file found"
    fi
}

docker_start() {
    check_env
    
    echo -e "${GREEN}Starting TPS19 with Docker...${NC}"
    docker-compose up -d
    
    echo -e "${GREEN}Services started:${NC}"
    docker-compose ps
}

docker_stop() {
    echo -e "${YELLOW}Stopping Docker services...${NC}"
    docker-compose down
}

docker_logs() {
    docker-compose logs -f tps19
}

backup() {
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backups/backup_${timestamp}"
    
    echo -e "${GREEN}Creating backup...${NC}"
    mkdir -p "$backup_dir"
    
    # Backup data
    if [ -d "data" ]; then
        cp -r data "$backup_dir/"
    fi
    
    # Backup logs
    if [ -d "logs" ]; then
        cp -r logs "$backup_dir/"
    fi
    
    # Backup environment (without secrets)
    if [ -f ".env" ]; then
        grep -v -E "(API_KEY|SECRET|PASSWORD)" .env > "$backup_dir/.env.sanitized"
    fi
    
    echo -e "${GREEN}Backup created: $backup_dir${NC}"
}

# Main script
print_banner

case "$1" in
    setup)
        setup
        ;;
    start)
        start "$2"
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start "$2"
        ;;
    status)
        status
        ;;
    test)
        test
        ;;
    logs)
        logs
        ;;
    docker-start)
        docker_start
        ;;
    docker-stop)
        docker_stop
        ;;
    docker-logs)
        docker_logs
        ;;
    backup)
        backup
        ;;
    *)
        echo "Usage: $0 {setup|start|stop|restart|status|test|logs|backup}"
        echo "       $0 {docker-start|docker-stop|docker-logs}"
        echo ""
        echo "Commands:"
        echo "  setup         - Initial setup and dependency installation"
        echo "  start         - Start TPS19 in simulation mode"
        echo "  start --live  - Start TPS19 in LIVE TRADING mode (dangerous!)"
        echo "  stop          - Stop TPS19"
        echo "  restart       - Restart TPS19"
        echo "  status        - Check if TPS19 is running"
        echo "  test          - Run system tests"
        echo "  logs          - View logs (tail -f)"
        echo "  backup        - Create backup of data and logs"
        echo ""
        echo "Docker commands:"
        echo "  docker-start  - Start all services with Docker"
        echo "  docker-stop   - Stop all Docker services"
        echo "  docker-logs   - View Docker logs"
        exit 1
        ;;
esac