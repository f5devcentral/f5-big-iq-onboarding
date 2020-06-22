BIG-IQ Onboarding with Docker and Ansible
-----------------------------------------

Performs series of on-boarding steps to bootstrap a BIG-IQ system
to the point that it can accept configuration.

This can be used for **lab**, **proof of concept** or **production** BIG-IQ deployments **version 7.1**.

<p align="center"><a href="https://www.youtube.com/watch?v=U8RZ_lw19Gs" target=”_blank”>Watch the Video Tutorial<br/>
<img width="20%" height="20%" src="https://img.youtube.com/vi/U8RZ_lw19Gs/0.jpg"></a></p>

![Deployment Diagram](./images/diagram_onboarding.png)

Once the inventory hosts file is set with the necessary information (IP, license, dns, ntp, ...), 
the Ansible playbooks can be launched from your local machine or a remote linux machine, as long as you 
have network connectivity to the management IP addresses of the targeted BIG-IQ instances to onboard/configure.

Consult the [Planning and Implementing a BIG-IQ Centralized Management Deployment](https://techdocs.f5.com/en-us/bigiq-7-1-0/planning-and-implementing-big-iq-deployment.html) for details.

Instructions
------------

1. Choose the number of BIG-IQ CM and DCD you aim to deploy.

   **Examples**:
    - 1 BIG-IQ CM standalone, 1 BIG-IQ DCD
    - 1 BIG-IQ CM standalone, 2 BIG-IQ DCDs
    - 2 BIG-IQ CMs HA, 3 BIG-IQ DCDs

2. Deploy BIG-IQ instances in your environment.

    - [VMware](https://downloads.f5.com/esd/product.jsp?sw=BIG-IQ&pro=big-iq_CM)
    - [OpenStack](https://downloads.f5.com/esd/product.jsp?sw=BIG-IQ&pro=big-iq_CM)
    - [HyperV](https://downloads.f5.com/esd/product.jsp?sw=BIG-IQ&pro=big-iq_CM)
    - [AWS](https://aws.amazon.com/marketplace/pp/B00KIZG6KA?qid=1495059228012&sr=0-1&ref_=srh_res_product_title)
    - [Azure](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/f5-networks.f5-big-iq?tab=Overview)

    Go to the [BIG-IQ Knowledge Center](https://support.f5.com/csp/knowledge-center/software/BIG-IQ?module=BIG-IQ%20Centralized%20Management&version=7.1.0) and follow the setup guide.

    **ONLY for Public Cloud deployments** ([AWS](https://techdocs.f5.com/kb/en-us/products/big-iq-centralized-mgmt/manuals/product/big-iq-centralized-management-and-amazon-web-services-setup-6-0-0.html)/[Azure](https://techdocs.f5.com/kb/en-us/products/big-iq-centralized-mgmt/manuals/product/big-iq-centralized-management-and-msft-azure-setup-6-0-0.html)):

    - Deploy the instances with min 2 NICs (**REQUIRED** even if you are not using the 2nd Network Interface)
    - m4.2xlarge (AWS) and Standard_D8_v3 (Azure) are instances type recommended
    - Create EIPs and assign them to the primary interfaces for each CM and DCD instances
    - Make sure you have the private key of the Key Pairs selected
    - Copy your private key in the under the ~/.ssh directory and apply correct permission chmod 600 privatekey.pem in your linux machine you will use to run the tool
    - Configure the network security group for the ingress rules on each instances
    - Wait approximately 6 minutes before logging in

      *Example for AWS: (10.192.75.0/24 = VPC subnet, 34.132.183.134/32 = [your public IP](https://www.whatismyip.com))*

      Ports | Protocol | Source 
      ----- | -------- | ------
      | 0-65535 | tcp | 10.192.75.0/24 |
      | All traffic | all | 34.132.183.134/32 |      
  
3. From a machine with access to the BIG-IQ instances.

    - Install [Docker](https://docs.docker.com/engine/install/)
    - Install Git ([Linux](https://git-scm.com/download/linux) or [Windows](https://git-scm.com/download/win))

    Example for [Amazon Linux EC2 instance](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html):
    ```
    sudo yum update -y
    sudo amazon-linux-extras install docker git -y
    sudo service docker start
    sudo yum install git -y
    docker --version
    git --version
    ```

    Example for Ubuntu instance:
    ```
    sudo apt update
    sudo apt install docker.io containerd git -y
    sudo systemctl start docker
    sudo systemctl enable docker
    docker --version
    git --version
    ```

4. Clone the repository:

    ```
    git clone https://github.com/f5devcentral/f5-big-iq-onboarding.git
    ```

5. Edit the ansible inventory hosts file using your favorite editor and enter necessary information 
   (management IP, self IPs if needed, license, master key, root & admin passwords...).

    ```
    cd f5-big-iq-onboarding
    vi hosts
    ```

    Notes:
    
    - When setting up BIG-IQ HA, the host with haprimary=False needs to be the first listed.
    - Use ``bigiq_onboard_license_key=skipLicense:true`` for BIG-IQ DCD (only >= 7.1).
    - It is not recommended to set ``discoveryip`` for deployment in AWS or Azure (the management IP address will be used automatically if not set). 
    - ``ansible_host`` in AWS and Azure should be the private IP address assigned to eth0 (**DO NOT** use the public IP).


6. Build the Ansible docker images containing the F5 Ansible Galaxy roles.

    ```
    sudo docker build -t f5-big-iq-onboarding .
    ```

7. Validate Docker and Ansible are working correctly.

    ```
    sudo docker run -t f5-big-iq-onboarding ansible-playbook --version
    ```

    Ansible version should be displayed.

8. **VMware/OpenStack/HyperV**: In case you need to set/change the management IP address(es).

    ```
    tmsh modify sys global-settings mgmt-dhcp disabled
    tmsh create sys management-ip x.y.z.w/24
    tmsh save sys config
    ```

9. **AWS only**: Change default shell on all instances to bash, and set the admin's password to admin.
   SSH to each instances and run these tmsh commands (replace the IP addresses with the eth0 internal IP addresses of each instances):

    ```
    declare -a ips=("10.1.1.27" "10.1.1.20")
    newpassword="admin"
    privkey="~/.ssh/privatekey.pem"
    for ip in "${ips[@]}"
    do
        ssh -o StrictHostKeyChecking=no -i $privkey admin@$ip modify auth user admin password $newpassword
        ssh -o StrictHostKeyChecking=no -i $privkey admin@$ip modify auth user admin shell bash
        ssh -o StrictHostKeyChecking=no -i $privkey admin@$ip tmsh save sys config
    done
    ```

10. Execute the BIG-IQ onboarding playbooks.

    ```
    ./ansible_helper ansible-playbook /ansible/bigiq_onboard.yml -i /ansible/hosts
    ```

    Make sure the playbook PLAY RECAP is not returning any failure. 

11. Open BIG-IQ CM in a web browser by using the management private or public IP address with https, for example: ``https://<bigiq_mgt_ip>``.

12. If you have 2 BIG-IQ CMs, go to the [BIG-IQ Knowledge Center](https://techdocs.f5.com/en-us/bigiq-7-0-0/creating-a-big-iq-high-availability-auto-fail-over-config.html) to configure HA.

13. Verify connectivity between BIG-IQ CM, DCD and BIG-IPs. SSH to the BIG-IQ CM primary and execute.

    ```
    mkdir /shared/scripts
    cd /shared/scripts
    curl https://raw.githubusercontent.com/f5devcentral/f5-big-iq-pm-team/master/f5-bigiq-connectivityChecks/f5_network_connectivity_checks.sh > f5_network_connectivity_checks.sh
    chmod +x f5_network_connectivity_checks.sh
    ./f5_network_connectivity_checks.sh
    ```

    Note: Default user will be root but you can use different one (e.g. admin), in this case run: ``./f5_network_connectivity_checks.sh admin admin``

14. [Determine how much space you need on each of the volumes your BIG-IQ system uses](https://techdocs.f5.com/en-us/bigiq-7-1-0/big-iq-sizing-guidelines/dcd-sizing-guidelines.html#dcd-sizing-guidelines) (*optional*)

15. [Resizing Disk Space on BIG-IQ Virtual Edition](https://techdocs.f5.com/en-us/bigiq-7-1-0/big-iq-sizing-guidelines/resizing-disk-space-on-big-iq-virtual-edition.html) (*optional*)

16. Import [BIG-IQ AS3 Templates](https://github.com/f5devcentral/f5-big-iq) (*optional*)

17. Start managing BIG-IP devices from BIG-IQ, go to the [BIG-IQ Knowledge Center](https://techdocs.f5.com/en-us/bigiq-7-1-0/managing-big-ip-devices-from-big-iq/device-discovery-and-basic-management.html).

For more information, go to the [BIG-IQ Knowledge Center](https://support.f5.com/csp/knowledge-center/software/BIG-IQ?module=BIG-IQ%20Centralized%20Management&version=7.1.0).


Miscellaneous
-------------

- **LAB/POC only**: Disable SSL authentication for SSG or VE creation in VMware:

  ```
  echo >> /var/config/orchestrator/orchestrator.conf
  echo 'VALIDATE_CERTS = "no"' >> /var/config/orchestrator/orchestrator.conf
  bigstart restart gunicorn
  bigstart restart restjavad
  ```

  *Note: This parameter added to the orchestrator.conf is NOT preserves during BIG-IQ upgrade.*

Troubleshooting
---------------

- If you want to know what is happening when a Playbook runs, provide the **-vvvv** argument to the ansible-playbook command.

    ```
    ./ansible_helper ansible-playbook /ansible/bigiq_onboard.yml -i /ansible/hosts -vvvv
    ```

- If you get the error *"Failed to license the device"*, make sure your BIG-IQ instances have access to the F5 license server (Internet).

- Below error can be ignored.

    ```
    TASK [bigiq_onboard : Test authentication - old or new credentials] ****************************************************************************************************************
    fatal: [bigiq-dcd-1.lab.local]: FAILED! => {"cache_control": "no-store, no-cache, must-revalidate", "changed": false, "connection": "close", "content": "{\"code\":401,\"message\":\"Authentication failed.\",\"originalRequestBody\":\"{\\\"username\\\":\\\"admin\\\", ...hn/login"}
    ...ignoring
    ```

- If you get the error *"insufficient permissions"*, follow [K13380](https://support.f5.com/csp/article/K13380) to setup NTP on your BIG-IQ instances, then re-run the playbook.

- In case you need to restore the BIG-IQ system to factory default settings, follow [K15886](https://support.f5.com/csp/article/K15886) article.

- In case you need to force remove a DCD association from BIG-IQ, follow [K02014651](https://support.f5.com/csp/article/K02014651) article.

- If you encounter *ModuleNotLicensed:LICENSE INOPERATIVE:Standalone* on the DCD CLI, it can be ignored (when using skipLicense:true).

### Copyright

Copyright 2020 F5 Networks Inc.

### License

#### Apache V2.0

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.

#### Contributor License Agreement

Individuals or business entities who contribute to this project must have
completed and submitted the [F5 Contributor License Agreement](http://f5-openstack-docs.readthedocs.io/en/latest/cla_landing.html).
