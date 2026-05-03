# ☁️ AWS EC2 Free Tier Deployment Guide
## Digital Legacy Platform

This guide will walk you through deploying the Digital Legacy Platform on Amazon Web Services (AWS) using their 12-month Free Tier.

---

## Step 1: Create an AWS Account
1. Go to [aws.amazon.com](https://aws.amazon.com/) and create a free account.
2. You will need a credit/debit card to verify your identity, but you won't be charged if you stay within the free tier limits.

## Step 2: Launch an EC2 Instance (Virtual Server)
1. In the AWS Management Console, search for **EC2** and click on it.
2. Click the orange **"Launch Instance"** button.
3. **Name:** Enter `digital-legacy-server`.
4. **Application and OS Image (AMI):** Select **Ubuntu**, then choose `Ubuntu Server 24.04 LTS (HVM)` (ensure it says "Free tier eligible").
5. **Instance Type:** Keep `t2.micro` (Free tier eligible). It has 1 vCPU and 1GB RAM.
   *Note: 1GB RAM is quite small for running PostgreSQL, Redis, Django, Celery, and Nginx all at once. We will need to configure a swap file later to prevent the server from crashing out of memory.*
6. **Key Pair (Login):** 
   - Click **"Create new key pair"**.
   - Name it `digital-legacy-key`.
   - Key pair type: `RSA`, Private key file format: `.pem`.
   - Click Create. It will download the `.pem` file to your computer. **Keep this safe!**
7. **Network Settings:**
   - Check **"Allow SSH traffic from"** (Anywhere).
   - Check **"Allow HTTP traffic from the internet"**.
   - Check **"Allow HTTPS traffic from the internet"**.
8. **Configure Storage:** Increase it from 8GB to **30GB** (30GB is the maximum allowed on the free tier).
9. Click **"Launch Instance"**.

## Step 3: Connect to your Server
1. Wait for your instance state to say "Running".
2. Select your instance and click the **"Connect"** button at the top.
3. You can either use "EC2 Instance Connect" (works right in the browser) or use the SSH client tab instructions to connect via your terminal using the `.pem` file you downloaded.

---

## Step 4: Prepare the Server (Inside the EC2 Terminal)

Since the `t2.micro` only has 1GB of RAM, we **must** create a Swap File, or Docker will crash when building the images.

Run these commands in your EC2 terminal exactly as written:

```bash
# 1. Update the server
sudo apt update && sudo apt upgrade -y

# 2. Create a 2GB Swap file to prevent Out-Of-Memory errors
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 3. Make the swap file permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 4. Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin -y

# 5. Allow your user to run docker without "sudo"
sudo usermod -aG docker ubuntu
```
*Note: You may need to log out and log back in (or close the EC2 connect window and reopen) for the Docker permissions to take effect.*

---

## Step 5: Get Your Code and Configure

```bash
# 1. Clone your repository from GitHub
git clone https://github.com/Azzurmawiy/digital-legacy-web.git
cd digital-legacy-web

# 2. Copy the example environment variables
cp .env.example .env

# 3. Edit the .env file
nano .env
```

Inside the `.env` file, you need to change a few things:
- Set `DEBUG=False`
- Set `ALLOWED_HOSTS=YOUR_EC2_PUBLIC_IP_ADDRESS` (You can find your Public IPv4 address in the AWS EC2 Console).
- Generate a secure `SECRET_KEY` and `MASTER_ENCRYPTION_KEY`.
- *(Press `Ctrl+X`, then `Y`, then `Enter` to save and exit nano).*

---

## Step 6: Launch!

Now we build and run the production environment. This step might take 5-10 minutes because the server is small.

```bash
# Build and start the containers
docker compose -f docker-compose.prod.yml up --build -d

# Run database migrations
docker compose -f docker-compose.prod.yml exec api python manage.py migrate

# Create your admin account
docker compose -f docker-compose.prod.yml exec api python manage.py createsuperuser
```

Once that finishes, you can type your EC2 Public IP address into your web browser, and your Digital Legacy Platform will be live!
