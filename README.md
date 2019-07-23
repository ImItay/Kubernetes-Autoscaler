# Kubernetes-Autoscaler
Kubernetes autoscaler script to manually manage the pods scaling

To use, replace all occurrences of "php-apache-manual" with your deployment's name

# Usage:
python scaler.py --target-cpu 75 --max-pods 5 --verbose 1
