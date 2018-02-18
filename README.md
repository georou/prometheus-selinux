# prometheus-selinux

**This policy is designed to be a base to build upon.** There are a lot of different configuration options for Prometheus and so I can't cover every aspect. 

The current policy allows you to setup a Prometheus server and scrape targets. Anything extra and you will need to add them into your policy. I am happy for pull requests to add features if you've already done them.

Also to note, this policy uses /opt and /opt/prometheus/data as locations for its files and TSDB.

## Installation
```sh
# Clone the repo
git clone https://github.com/georou/prometheus-selinux.git

# Compile the selinux module (see below)

# Install the SELinux policy module. Compile it before hand to ensure proper compatibility (see below)
semodule -i prometheusd.pp

# Restore all the correct context labels
restorecon -RvF /etc/prometheus
restorecon -RvF /opt/prometheus

# Start prometheusd
systemctl start prometheus-server.service

# Ensure it's working in the proper confinement
ps -eZ | grep prometheus
```

## How To Compile The Module Locally (Needed before installing)
Ensure you have the `selinux-policy-devel` package installed.
```sh
# Ensure you have the devel packages
yum install selinux-policy-devel setools-console
# Change to the directory containing the .if, .fc & .te files
cd prometheus-selinux
make -f /usr/share/selinux/devel/Makefile prometheusd.pp
semodule -i prometheusd.pp
```

## Debugging and Troubleshooting

* If you're getting permission errors, uncomment permissive in the .te file and try again. Re-check logs for any issues. Or `semanage permissive -a prometheusd_t`
* Easy way to add in allow rules is the below command, then copy or redirect into the .te module. Rebuild and re-install:
* Don't forget to actually look at what is suggested. audit2allow will most likely go for a coarse grained permission!

```sh
ausearch -m avc,user_avc,selinux_err -ts recent | audit2allow -R
```
If you get a could not open interface info [/var/lib/sepolgen/interface_info] error. 
Ensure policycoreutils-devel is installed and/or run: `sepolgen-ifgen`

## Compatibility Notes
Built on CentOS 7.4 at the time with:
```
selinux-policy-targeted-3.13.1-166.el7_4.7.noarch
selinux-policy-3.13.1-166.el7_4.7.noarch
selinux-policy-devel-3.13.1-166.el7_4.7.noarch
```
