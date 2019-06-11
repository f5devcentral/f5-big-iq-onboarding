# Ansible Role: BIG-IQ Register DCD

Performs a series of steps needed to register a BIG-IQ provisioned as a Data Collection
Device (DCD) to a BIG-IQ provisioned as a Configuration Management (CM) device.

## Requirements

None.

## Role Variables

Available variables are listed below. For their default values, see `defaults/main.yml`:

    register_dcd_cm_server: localhost
    register_dcd_cm_server_port: 443
    register_dcd_cm_user: admin
    register_dcd_cm_password: secret
    register_dcd_cm_validate_certs: false
    register_dcd_cm_transport: rest
    register_dcd_cm_timeout: 120

Establishes initial connection to your BIG-IQ. These values are substituted into
your ``provider`` module parameter. These values should be the connection parameters
for the **CM BIG-IP** device.

    register_dcd_dcd_user: admin
    
Username to use when logging in to the DCD device. This value is sent to the CM device
during DCD node registration. The CM needs to communicate with the DCD device to register
it. This credential is required to do that.

    register_dcd_dcd_password: secret

Password of the user used to connect to DCD device. This value is sent to the CM device
during DCD node registration. The CM needs to communicate with the DCD device to register
it. This credential is required to do that.

    register_dcd_dcd_server: localhost

The IP address of the DCD server to register. This value is required so that the CM device
will know which DCD to register. Depending on your method for registering DCD devices, you
may want to simply set this to be the ``ansible_host`` variable of the DCD host.

    register_dcd_dcd_listener: localhost

The IP address that the DCD will listen for events on. By default, this address is the same
address that is specified in ``register_dcd_dcd_server``.

    register_dcd_dcd_services:
      - access
      - dos
      - websafe
      - ipsec
      - afm
      - asm

List of services that you want activated for the DCD. By default, we activate all of the
available services. You can override this on a group or host-based level depending on the
needs of the DCD device.

## Dependencies

* A BIG-IQ that has been onboarded. This can be accomplished in a number of ways, including
  via the use of the [bigiq_onboard][1] Ansible Galaxy role.
* Alternatively, you can set the ``isSystemSetup`` attribute on the BIG-IQ (found at the
  API endpoint ``/mgmt/shared/system/setup``) to ``true``.

## Example Playbook

There are two ways that you can use this role due to the variables that you can specify.

The choice of which method is up to you. Consider though that the concurrent method
will usually be faster. Where-as the serial method is easier for people new to Ansible
to understand (because it does not take advantage of Ansible's native concurrency).

* Concurrently
* Serially

Examples of each are shown below.

### Concurrently

In the concurrent setup, take note of the ``hosts`` line in the example Play. By
specifying the DCD nodes in the host line, you take advantage of Ansible's implicit
concurrency. Each DCD node will (concurrently) attempt to register itself with the
CM.

The ``register_dcd_dcd_server`` we provide to the role is the IP address of the DCD
host.

    - name: Add DCD devices to CM device concurrently
      hosts: dcd
      vars_files:
        - vars/main.yml
      tasks:
        - name: Add DCD to CM
          include_role:
            name: f5devcentral.register_dcd
          vars:
            register_dcd_dcd_server: "{{ ansible_host }}"

### Serially

In the serial setup, take note of the ``hosts`` line in the example Play. The
``hosts`` line in this example only specifies the CM device. The consequence of
this is that each DCD node will need to be added by using a loop in Ansible.

No concurrency happens in this example. DCD nodes are added one at a time in the
loop. 

The ``register_dcd_dcd_server`` is populated by looking up the ``ansible_host``
variable of the DCD host. DCD hosts are grouped in a ``dcd`` group so that they
can easily be looped over.

    - name: Add DCD devices to CM device serially
      hosts: cm
      vars_files:
        - vars/main.yml
      tasks:
        - name: Add DCD to CM
          include_role:
            name: f5devcentral.register_dcd
          vars:
            register_dcd_dcd_server: "{{ hostvars[item].ansible_host }}"
          loop: "{{ groups['dcd'] }}"

*Inside `vars/main.yml`*:

    register_dcd_cm_server: bigiq-cm01.domain.org
    register_dcd_cm_password: secret
    register_dcd_dcd_password: secret

## License

Apache

## Author Information

This role was created in 2018 by [Tim Rupp](https://github.com/caphrim007).

[1]: https://galaxy.ansible.com/f5devcentral/bigiq_onboard
