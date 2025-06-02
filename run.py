import argparse
import os
from dotenv import load_dotenv
import uvicorn
import logging

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run the server in different modes.")
    parser.add_argument("--prod",action="store_true", help="Run the server in production mode.")
    parser.add_argument("--uat",action="store_true", help="Run the server in uat mode.")
    parser.add_argument("--sit",action="store_true", help="Run the server in sit mode.")
    
    args = parser.parse_args()

    if args.prod:
        load_dotenv("app/core/.env.prod")
    elif args.uat:
        load_dotenv("app/core/.env.uat")
    elif args.sit:
        load_dotenv("app/core/.env.sit")
    else:
        load_dotenv("app/core/.env.dev")

    debug=True if os.getenv("ENV") == "dev" else False

    logging.warning(f"Debug mode: {debug}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=3000, reload=True)