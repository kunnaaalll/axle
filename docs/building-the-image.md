# Building the AXLE AMI (T-160, T-162)

To deploy the AXLE framework natively across the globe, we rely on **HashiCorp Packer** to compile the pristine Ubuntu baseline into a deployable Amazon Machine Image (AMI).

## Execution Sequence

1. **Prerequisites**
   Ensure you have AWS CLI configured and Packer installed locally.
   ```bash
   aws configure
   packer version
   ```

2. **Initialize Packer**
   Enter the core build registry:
   ```bash
   cd build/packer
   packer init .
   ```

3. **Validation Run**
   Validate the JSON/HCL configurations to ensure syntax compliance:
   ```bash
   packer validate ubuntu-axle.pkr.hcl
   ```

4. **Compile the Image**
   This triggers an ephemeral EC2 instance, applies all `.sh` provisioning scripts, and commits the host drive to an AMI.
   ```bash
   packer build ubuntu-axle.pkr.hcl
   ```

## Next Steps
Once the AMI is packaged, map the new `ami-xxx` identifier directly into your Terraform cluster configurations to deploy identical 1080p AXLE graphical servers on-demand.
