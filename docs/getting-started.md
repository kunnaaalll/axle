# Getting Started with AXLE OS

Welcome to AXLE OS. This guide will help you get your deployment appliance up and running.

## Prerequisites
- An AWS Account (for Phase 1)
- SSH Key Pair
- AI Provider API Key (Gemini, OpenAI, or a local Ollama instance)

## Deployment Steps

1.  **Launch the AMI**: Find the AXLE OS AMI in the AWS Marketplace (or build your own using our Packer scripts).
2.  **Initial Connection**: SSH into your instance.
    ```bash
    ssh ubuntu@<your-ec2-ip>
    ```
3.  **Run Setup**: Follow the on-screen prompts or run:
    ```bash
    axle setup
    ```
4.  **Access Dashboard**: Open `http://<your-ec2-ip>:4000` in your browser.

## Deploying Your First App

1.  Go to the "Deploy" tab in the dashboard.
2.  Paste your GitHub repository URL.
3.  Review the AI-generated deployment plan.
4.  Click "Confirm Deployment".
5.  Watch the live logs as AXLE configures your server!
