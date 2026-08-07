import os
import pytest


def test_terraform_iac_artifacts_exist():
    """Test Terraform IaC manifests exist."""
    assert os.path.exists("deploy/terraform/main.tf")


def test_helm_chart_artifacts_exist():
    """Test Kubernetes Helm chart manifests exist."""
    assert os.path.exists("deploy/helm/Chart.yaml")
    assert os.path.exists("deploy/helm/values.yaml")
    assert os.path.exists("deploy/helm/templates/deployment.yaml")


def test_operational_runbooks_and_guides_exist():
    """Test production deployment guide and incident runbooks exist."""
    assert os.path.exists("docs/DEPLOYMENT_GUIDE.md")
    assert os.path.exists("docs/RUNBOOKS.md")
