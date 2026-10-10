devops-demo

A small Flask app used to walk through the full DevOps chain end to end on a local Ubuntu VM: code, container, CI pipeline, security scan, infrastructure as code, Kubernetes, monitoring and configuration management.

The app is deliberately tiny. The point of the project is everything around it.

About this project

This was my first full run-through of the DevOps chain, and I was guided through it step by step by Claude (an AI assistant made by Anthropic). I typed and ran every command myself on my own VM, fixed the errors that came up, and built the whole thing end to end. It is a learning project, not production work. Next I am going back through each stage in depth over a 12-week plan and will rebuild the pieces without step-by-step guidance.

The flow
code --> Git/GitHub --> GitHub Actions (build, test, scan) --> Docker image
                                                                   |
        Terraform (infrastructure as code) --> Kubernetes (runs and heals it)
                                                                   |
                          Prometheus + Grafana (monitoring)    Ansible (server config)
What is in this repo
Path	What it is
app.py	Flask app with two endpoints: / (message) and /health (health check)
requirements.txt	Python dependencies
Dockerfile	Builds the app into a container image
.github/workflows/ci.yml	CI pipeline: build, smoke test, Trivy scan
tf/main.tf	Terraform: runs the container through the Docker provider
monitoring/	Docker Compose stack: Prometheus, node-exporter, Grafana
ansible/playbook.yml	Ansible playbook: installs and configures nginx
Lab environment
Ubuntu 22.04 VM, 40 GB disk
Docker, Docker Compose, Terraform, AWS CLI, kubectl, minikube, Helm, Trivy, Ansible, Git
How to run each stage
1. The app in Docker
bash
docker build -t devops-demo:1.0 .
docker run -d -p 5000:5000 --name demo devops-demo:1.0
curl localhost:5000
curl localhost:5000/health
docker rm -f demo
2. Security scan
bash
trivy image devops-demo:1.0
3. CI pipeline

Runs automatically on every push to main. It:

Checks out the code
Builds the image, tagged with the commit SHA
Starts the container and calls /health (the pipeline fails if it does not answer)
Scans the image with Trivy (reports HIGH and CRITICAL findings, does not block yet)
4. Terraform
bash
cd tf
terraform init
terraform plan
terraform apply
curl localhost:5001
terraform destroy
5. Kubernetes (minikube)
bash
minikube start --driver=docker
minikube image load devops-demo:1.0
kubectl create deployment demo --image=devops-demo:1.0 --port=5000
kubectl expose deployment demo --type=NodePort --port=5000
curl $(minikube service demo --url)

# self-healing: scale up, delete a pod, watch it get replaced
kubectl scale deployment demo --replicas=3
kubectl get pods
kubectl delete pod <pod-name>
kubectl get pods

# clean up
kubectl delete deployment demo
kubectl delete service demo
minikube stop
6. Monitoring
bash
cd monitoring
docker compose up -d
Prometheus targets: http://localhost:9090/targets
Grafana: http://localhost:3000 (import dashboard ID 1860 for a full host dashboard)
bash
docker compose down
7. Ansible
bash
cd ansible
ansible-playbook -i localhost, playbook.yml -K

Run it twice. The second run reports no changes, because Ansible only fixes what differs.

What each tool is for
Git/GitHub: history of every change, and the trigger for automation
Docker: packages the app so it runs the same everywhere
GitHub Actions: runs build, test and scan on every push so nobody has to remember
Trivy: finds known vulnerabilities in the image
Terraform: describes infrastructure in code so it is repeatable
Kubernetes: runs several copies and replaces any that die
Prometheus and Grafana: show CPU, memory, disk and service health
Ansible: configures servers identically from one file
Problems I hit and how I fixed them
Problem	Cause	Fix
minikube start failed with "no space left on device"	VM disk was full from images, installers and downloads	Moved to a larger disk
New VM still showed a ~12 GB root partition on a 40 GB disk	The partition was not using the whole disk	growpart /dev/sda 1 then resize2fs /dev/sda1
apt upgrade failed on the Firefox package ("device not yet seeded")	Snap had not finished its first-time setup	Waited for snap to seed, restarted snapd, then dpkg --configure -a and apt --fix-broken install
apt install -y reported "-y is an invalid option"	Copy and paste turned the hyphen into a long dash	Retyped the option, or replaced the characters with sed
docker needed sudo after adding my user to the group	Group membership only applies on a new login	Logged out fully and back in (reboot)
minikube start --drive=docker rejected	Typo, the flag is --driver	Corrected the flag
sudo install terraform failed	Missing apt, so it ran the file-copy command	sudo apt install terraform
Next steps
Make Trivy fail the pipeline on critical findings
Push the image to a container registry from the pipeline
Add a database and a reverse proxy with Docker Compose
Replace the Docker provider in Terraform with AWS (VPC, EC2, security group)
Deploy to Kubernetes with Helm
Add an alert in Grafana for when the app goes down
