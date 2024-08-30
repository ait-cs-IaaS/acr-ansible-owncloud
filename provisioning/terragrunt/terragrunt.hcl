# Save the Terraform state in a shared location, that everyone can access it. 
remote_state {
  backend = "http"
  config = {
    address        = "https://git-service.ait.ac.at/api/v4/projects/2197/terraform/state/${get_env("OS_PROJECT_NAME")}_${get_env("OS_USER_DOMAIN_NAME")}_${path_relative_to_include()}_${basename(get_repo_root())}"
    lock_address   = "https://git-service.ait.ac.at/api/v4/projects/2197/terraform/state/${get_env("OS_PROJECT_NAME")}_${get_env("OS_USER_DOMAIN_NAME")}_${path_relative_to_include()}_${basename(get_repo_root())}/lock"
    unlock_address = "https://git-service.ait.ac.at/api/v4/projects/2197/terraform/state/${get_env("OS_PROJECT_NAME")}_${get_env("OS_USER_DOMAIN_NAME")}_${path_relative_to_include()}_${basename(get_repo_root())}/lock"
    username       = "${get_env("GITLAB_USERNAME")}"
    password       = "${get_env("CR_GITLAB_ACCESS_TOKEN")}"
    lock_method    = "POST"
    unlock_method  = "DELETE"
    retry_wait_min = "5"
  }
}

terraform {
  source = "."

  extra_arguments "parallelism" {
    commands  = ["apply"]
    arguments = ["-parallelism=${get_env("TF_VAR_parallelism", "10")}"]
  }

  extra_arguments "conditional_vars" {
    commands = ["apply", "plan", "refresh", "destroy"]
    optional_var_files = [
      "${get_terragrunt_dir()}/${get_env("TF_VAR_env", "")}.tfvars",
      "${get_parent_terragrunt_dir()}/${get_env("TF_VAR_env", "")}.tfvars"
    ]
  }
}


inputs = {
  public_router = "${get_env("OS_PROJECT_NAME")}-router"
  #project = "demo"
  teams = [
    {
      name         = "cbt"
      domain       = "cbt.at"
      display_name = "cbt"
      password     = "mozart.rocks"
      cloud     = true
    },
    {
      name         = "dev"
      domain       = "dev.at"
      display_name = "dev"
      password     = "mozart.rocks"
      cloud     = true
    },
  ]
}