# Kubernetes-Autoscaler
Kubernetes autoscaler script to manually manage the pods scaling

In order to use, replace all occurrences of __"php-apache-manual"__ with your deployment's name

# Usage:
```scaler.py --target-cpu 75 --max-pods 5 --verbose 1```

__--target-cpu:__ set the target CPU percentage to maintain

__--max-pods:__ set maximum allowed pods for the deployment

__--verbose:__ set to 1 to view the log output
