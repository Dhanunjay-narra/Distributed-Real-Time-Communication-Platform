import os, yaml

def test_infrastructure_manifests_validity():
    manifests = [
        "deploy/k8s/namespace.yaml",
        "deploy/k8s/deployments.yaml",
        "deploy/k8s/ingress.yaml",
        "deploy/k8s/hpa.yaml",
        "deploy/helm/Chart.yaml",
        "deploy/helm/values.yaml"
    ]
    for m in manifests:
        assert os.path.exists(m), f"Manifest {m} does not exist"
        with open(m, "r", encoding="utf-8") as f:
            docs = list(yaml.safe_load_all(f))
            assert len(docs) >= 1, f"No YAML documents in {m}"

    assert os.path.exists("deploy/terraform/main.tf")
    assert os.path.exists("deploy/terraform/variables.tf")
