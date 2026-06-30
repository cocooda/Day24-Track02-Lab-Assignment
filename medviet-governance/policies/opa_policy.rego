package medviet.data_access

import future.keywords.if
import future.keywords.in

default allow := false
default deny := false

deny if {
    input.data_classification == "restricted"
    input.destination_country != "VN"
}

base_allow if {
    input.user.role == "admin"
}

base_allow if {
    input.user.role == "ml_engineer"
    input.resource in {"training_data", "model_artifacts"}
    input.action in {"read", "write"}
}

base_allow if {
    input.user.role == "data_analyst"
    input.resource == "aggregated_metrics"
    input.action == "read"
}

base_allow if {
    input.user.role == "data_analyst"
    input.resource == "reports"
    input.action == "write"
}

base_allow if {
    input.user.role == "intern"
    input.resource == "sandbox_data"
    input.action in {"read", "write"}
}

allow if {
    base_allow
    not deny
}
