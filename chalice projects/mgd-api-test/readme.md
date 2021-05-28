**How to use**

* Provide yours AWS STS credentials
* Provide a default region with `export AWS_DEFAULT_REGION=<REGION>`
* Launch script with bash launch_test.sh <endpoint> <token>
* Just wait until tests are done

**TEST CATEGORIES**
The tests are divided into different categories:

- General resources tests: `Test_0*()` (* is the ID of general resource)
- Parameter validation (general resources) tests: `Test_pv_0#_0*()` (# rappresent number of test for that resource, * is the ID of general resource)
- Workflows tests: `Test_wf_0*()`
- Workflows tests - Step Function: `Test_wf_0*_SF()`
- Parameter validation (workflows) tests: `Test_pv_0#_wf_0*()` (# rappresent number of test for that workflow, * is the ID of workflow)

General Resources are:

  1. </datasets>
  2. </dataset/{id}/info>
  3. </dataset/{id}/wfs>
  4. </request>

Workflows are:

  1. </horta>
  2. </dataset/ecmwf/workflow/horta>
  3. </dataset/agmerra/workflow/pbdm>

**WARNING**
If you are using a Mac system, in order to use the launch_test.sh script, brew has to be pre-installed.
If brew is not installed on your machine, use `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"` in order to install it 