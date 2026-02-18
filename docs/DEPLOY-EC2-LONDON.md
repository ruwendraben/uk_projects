# Deploy to EC2 + ALB in London (eu-west-2)

This deploys your Django app to a **single t3.micro EC2 instance** behind an **Application Load Balancer** in **eu-west-2 (London)**. The app is reached via the **ALB DNS name** (e.g. `http://webserver-ec2-alb-xxxx.eu-west-2.elb.amazonaws.com`).

## What gets created

- **CloudFormation:** `ec2-webserver.yaml` → stack `webserver-ec2-staging`
- **EC2:** 1× t3.micro (free tier eligible), runs your app in Docker. Launched with SSH key **london-ec2** so you can log in.
- **ALB:** Listens on port 80, forwards to the app on port 8000
- **ECR:** Repository `webserver` in eu-west-2 (image built and pushed by the workflow)

## Before you run the workflow

### 1. GitHub repo secrets

In **Settings → Secrets and variables → Actions**, add:

| Secret name             | Description |
|-------------------------|-------------|
| `AWS_ACCESS_KEY_ID`      | IAM user access key with permissions below |
| `AWS_SECRET_ACCESS_KEY`  | IAM user secret key |

**Optional:** If your key pair has a different name, add secret `AWS_EC2_KEY_NAME` (e.g. `my-key-name`). Default is **london-ec2**.

The IAM user needs at least:

- `cloudformation:*`
- `ec2:*`
- `ecr:*`
- `elasticloadbalancing:*`
- `iam:CreateRole`, `iam:PutRolePolicy`, `iam:PassRole`, `iam:AttachRolePolicy`

(Easiest: use an IAM user with **AdministratorAccess** in a dedicated “deploy” AWS account or restrict to the above.)

### 2. Default VPC in eu-west-2

The workflow uses the **default VPC** and its subnets in **eu-west-2**. Ensure your AWS account has a default VPC in that region (it usually does). If not, create a VPC and subnets and pass them as extra parameters (workflow would need to be updated to use custom VPC/subnets).

### 3. Django ALLOWED_HOSTS

Your `webserver_project.settings` already has `ALLOWED_HOSTS = ['*']`, so the ALB hostname is allowed. If you change that later, add the ALB DNS name.

## How to deploy

1. In GitHub: **Actions** → **CI** → **Run workflow**
2. Choose branch **master**
3. Check **Deploy to staging** (and optionally **Deploy to production** after)
4. Click **Run workflow**

When the job finishes, the log will print **App URL** and **SSH** (public IP). Open the App URL in a browser to see your app.

### SSH into the instance

The instance is launched with key pair **london-ec2** (or the name in `AWS_EC2_KEY_NAME`). Use the matching `.pem` file:

```bash
# Use the public IP printed in the workflow log (or get it from EC2 console)
ssh -i london-ec2.pem ec2-user@<PUBLIC_IP>
```

- **User:** `ec2-user` (Amazon Linux 2)
- **Key:** `london-ec2.pem` (the private key you downloaded when creating the key pair in eu-west-2)

Ensure the key pair **london-ec2** exists in AWS **eu-west-2** (EC2 → Key Pairs). If you created it in another region, create or import it in eu-west-2.

## Updating the app

Re-run the workflow with **Deploy to staging** checked. The workflow will:

- Build a new image and push to ECR as `:latest`
- Update the CloudFormation stack (parameters)

**Note:** The EC2 instance runs the image only at **first boot** (from user data). To run a new image after you’ve already deployed, you must either:

- **Replace the instance** (e.g. change a CloudFormation property so the instance is replaced), or  
- **SSH or use SSM** to the instance and run `docker pull ... && docker stop app && docker run ...` (or add an SSM Run Command step to the workflow).

For a single staging instance, recreating the stack (delete stack, then run workflow again) also gives you a fresh instance with the latest image.

## Costs

- **EC2 t3.micro:** Free tier eligible (750 hrs/month for 12 months in a new account), then low cost in eu-west-2.
- **ALB:** Small hourly charge + data processing.
- **ECR:** Storage for the image (usually minimal).
