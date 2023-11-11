# 📘 Project Paper 2:  Integrating Arkouda with Pachyderm on Kubernetes

This repository encompasses both the project and its corresponding paper of my semester thesis. The primary focus is on the incorporation of the HPC framework Arkouda into the Kubernetes workflow orchestrator, Pachyderm. Moreover, this repository also details the setup of a 20-node on-prem cluster using Kubeadm and delineates the infrastructure's configuration and the establishment of the CI/CD pipeline.

## 📄 Paper

**Abstract:**

This Second project paper presents the development and demonstration of a proof-of-concept for the
integration of HPC programming frameworks in ta a container-base workflow orchestrator the convergence of
HPC and CC has revealed novel potential in highly scalable and flexible computing.

This project aim to reconcile the different demands of the HPC and CC communities by demonstrating the integration of
the HPC programming framework Arkouda into the container-based workflow orchestrator Pachyderm, showing the technical feasibility of this approach.

A prototype implementing this integrated system is constructed and evaluated through prototyping methodologies, with a focus on resilience, scalability, portability, and user-friendliness.
The prototype is iteratively refined to address LCP and TCP, with particular attention to the usability of the system for non CC experts.

This project paper contributes to the body of knowledge by way of practical example, lessons learned with each iteration, and sheds lith on pathways for future research towards
a landscape where the seamless and efficient integration of HPC workloads in CC environments becomes possible

The complete paper can be found here: \
📜 [Full Paper](DHBW/PA2/studienarbeit.pdf)

## 🛠  Project Documentation

This project was realized in collaboration with the Hewlett Packard Labs and signifies the stepping stone towards my bachelor's thesis.

💼 [Project Overview](Project/README.md)

## 🗝️ Key Aspects

The following sections highlight the key aspects of this project.

- The integration of Pachyderm and Arkouda
- The creation of a CI/CD pipeline using Forgejo, Jenkins, Kaniko
- Setup of a bare metal 20 node Kubernetes cluster using kubeadm

## 🙏 Acknowledgements

I extend my heartfelt gratitude to Dr. Harumi Kuno, a Principal Research Scientist at Hewlett Packard Labs, for her unwavering guidance and support throughout this journey. \
Her mentorship has been instrumental in shaping this project.

I would also like to acknowledge Sharad Singal, Senior Distinguished Technologist at Hewlett Packard Labs, for his leadership and vision. \
I'm equally grateful to my academic supervisor, Dominic Viola, for his invaluable insights and recommendations.

My sincere appreciation goes to the Hewlett Packard Labs for entrusting me with this remarkable project
and to Hewlett Packard Enterprise for their consistent support during my academic endeavors.
