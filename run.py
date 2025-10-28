from app import create_app

app = create_app()

if __name__ == '__main__':
    debug = True
    host = '0.0.0.0'
    port = 5000
    
    print("Starting Kaveri.ai Personalized Learning Engine")
    print(f"Debug Mode: {debug}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    
    app.run(host=host, port=port, debug=debug)