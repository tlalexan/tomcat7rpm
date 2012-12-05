%define servicename tomcat7

%define tomcat_home_dir   %{_datadir}/tomcat7
%define tomcat_cache_dir  %{_var}/cache/tomcat7
%define tomcat_shared_dir %{_sharedstatedir}/tomcat7
%define tomcat_logs_dir   %{_var}/log/tomcat7
%define tomcat_conf_dir   %{_sysconfdir}/tomcat7

%define tomcat_bin_dir     %{tomcat_home_dir}/bin
%define tomcat_lib_dir     %{tomcat_home_dir}/lib
%define tomcat_temp_dir    %{tomcat_cache_dir}/temp
%define tomcat_work_dir    %{tomcat_cache_dir}/work
%define tomcat_webapps_dir %{tomcat_shared_dir}/webapps

%define sysconfig_dir   %{_sysconfdir}/sysconfig
%define tomcat_sysconf_file %{sysconfig_dir}/%{servicename}

%define tomcat_user  tomcat
%define tomcat_group tomcat
%define java_home /usr/java/default

%define __jar_repack %{nil}

%define commonsdaemonversion 1.0.10

Name: apache-tomcat
Version: 7.0.33
Release: 1
Summary: Open source software implementation of the Java Servlet and JavaServer Pages technologies.
Group: Productivity/Networking/Web/Servers 
License: Apache Software License.
Url: http://tomcat.apache.org 
Source: http://www.us.apache.org/dist/tomcat/tomcat-7/v%{version}/bin/%{name}-%{version}.tar.gz


Requires: jdk

%description
Apache Tomcat is an open source software implementation of the Java Servlet and JavaServer Pages technologies. The Java Servlet and JavaServer Pages specifications are developed under the Java Community Process.

%prep
%setup 

%install
echo %{buildroot}
echo $RPM_BUILD_ROOT
rm -rf %{buildroot}

mkdir -p %{buildroot}%{tomcat_bin_dir}
cp bin/catalina-tasks.xml bin/tomcat-juli.jar bin/bootstrap.jar %{buildroot}%{tomcat_bin_dir}

mkdir -p %{buildroot}%{tomcat_lib_dir}
cp lib/* %{buildroot}%{tomcat_lib_dir}

mkdir -p %{buildroot}%{tomcat_temp_dir}
ln -sf %{tomcat_temp_dir} %{buildroot}%{tomcat_home_dir}/temp

mkdir -p %{buildroot}%{tomcat_work_dir}
ln -sf %{tomcat_work_dir} %{buildroot}%{tomcat_home_dir}/work

mkdir -p %{buildroot}%{tomcat_webapps_dir}
ln -sf %{tomcat_webapps_dir} %{buildroot}%{tomcat_home_dir}/webapps

mkdir -p %{buildroot}%{tomcat_logs_dir}
ln -sf %{tomcat_logs_dir} %{buildroot}%{tomcat_home_dir}/logs

mkdir -p %{buildroot}%{tomcat_conf_dir}
cp conf/catalina.policy %{buildroot}%{tomcat_conf_dir}
cp conf/catalina.properties %{buildroot}%{tomcat_conf_dir}
cp conf/context.xml %{buildroot}%{tomcat_conf_dir}
cp conf/logging.properties %{buildroot}%{tomcat_conf_dir}
cp conf/server.xml %{buildroot}%{tomcat_conf_dir}
cp conf/tomcat-users.xml %{buildroot}%{tomcat_conf_dir}
cp conf/web.xml %{buildroot}%{tomcat_conf_dir}
ln -sf %{tomcat_conf_dir} %{buildroot}%{tomcat_home_dir}/conf

mkdir -p %{buildroot}%{sysconfig_dir}
cat > %{buildroot}%{tomcat_sysconf_file} <<'END_OF_TOMCAT7_CONF'
# This will be sourced by %{servicename}
# Use this to change default values 

# Where your java installation lives
JAVA_HOME=%{java_home}

# Where your tomcat installation lives
CATALINA_BASE="%{tomcat_home_dir}"
CATALINA_HOME="%{tomcat_home_dir}"
JASPER_HOME="%{tomcat_home_dir}"
CATALINA_TMPDIR="%{tomcat_temp_dir}"

# You can pass some parameters to java here if you wish to
#JAVA_OPTS="-Xminf0.1 -Xmaxf0.3"

# What user should run tomcat
TOMCAT_USER="%{tomcat_user}"

# You can change your tomcat locale here
#LANG="en_US"

# If you wish to further customize your tomcat environment,
# put your own definitions here
# (i.e. LD_LIBRARY_PATH for some jdbc drivers)

END_OF_TOMCAT7_CONF


mkdir -p %{buildroot}%{_initddir}
cat > %{buildroot}%{_initddir}/%{servicename} <<'END_OF_TOMCAT7_INIT_SCRIPT'
#!/bin/bash
#
# %{_servicename}     Startup script for Apache Tomcat 6
#
# chkconfig: - 84 16
# description: Apache Tomcat is a java container
# config: /etc/%{servicename}/%{servicename}.conf
# pidfile: /var/run/%{servicename}.pid

TOMCAT_PID="/var/run/%{servicename}.pid"
TOMCAT_CONFIG="%{tomcat_sysconf_file}"

# Source function library.
. /etc/rc.d/init.d/functions

# Read config
[ ! -f "$TOMCAT_CONFIG" ] && echo "$TOMCAT_CONFIG does not exist!"
[ -f "$TOMCAT_CONFIG" ] && . "$TOMCAT_CONFIG"

# Make sure the required variable were set by the config 
[ -z "$JAVA_HOME" ] &&  echo "JAVA_HOME must be set" && exit 99;
[ -z "$CATALINA_HOME" ] &&  echo "CATALINA_HOME must be set" && exit 99;
[ -z "$CATALINA_BASE" ] &&  echo "CATALINA_BASE must be set" && exit 99;
[ -z "$CATALINA_TMPDIR" ] &&  echo "CATALINA_TMPDIR must be set" && exit 99;
[ -z "$TOMCAT_USER" ] &&  echo "TOMCAT_USER must be set" && exit 99;


BOOT_CLASSPATH=$CATALINA_HOME/bin/tomcat-juli.jar:$CATALINA_HOME/bin/bootstrap.jar:$CATALINA_HOME/lib/commons-daemon.jar

RETVAL=0

case "$1" in
    start)
        echo -n "Starting Tomcat"

    jsvc -home $JAVA_HOME \
        -pidfile $TOMCAT_PID \
        -outfile %{tomcat_logs_dir}/catalina.out \
        -errfile '&1' \
        -user $TOMCAT_USER \
        -cp $BOOT_CLASSPATH \
        -Dcatalina.base=$CATALINA_BASE \
        -Dcatalina.home=$CATALINA_HOME \
        -Djava.io.tmpdir=$CATALINA_TMPDIR \
        $JAVA_OPTS \
        org.apache.catalina.startup.Bootstrap start

    RETVAL=$?
        echo
        ;;
    stop)
        echo -n "Shutting down %{servicename}"
    jsvc -home $JAVA_HOME \
        -pidfile $TOMCAT_PID \
        -user $TOMCAT_USER \
        -cp $BOOT_CLASSPATH \
        -stop \
        org.apache.catalina.startup.Bootstrap

        RETVAL=$?
        echo
        ;;
    restart)
        $0 stop
        $0 start
        ;;
    status)
        status %{servicename}
        RETVAL=$?
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac
exit $RETVAL
END_OF_TOMCAT7_INIT_SCRIPT


cp bin/commons-daemon.jar %{buildroot}%{tomcat_lib_dir}
cd bin 
tar xf commons-daemon-native.tar.gz
cd commons-daemon-%{commonsdaemonversion}-native-src/unix
./configure --with-java=%{java_home}
make
mkdir -p %{buildroot}%{_sbindir}
cp jsvc %{buildroot}%{_sbindir}

%clean
rm -rf %{buildroot}

%pre
getent group %{tomcat_group} > /dev/null || groupadd -r %{tomcat_group}
getent passwd %{tomcat_user} > /dev/null || useradd -r -g %{tomcat_group} %{tomcat_user}
exit 0

%post

%preun
service %{servicename} status && service %{servicename} stop
exit 0

%files
%defattr(-,tomcat,tomcat,-)

%dir %{tomcat_bin_dir}
%{tomcat_bin_dir}/*

%dir %{tomcat_lib_dir}
%{tomcat_lib_dir}/*

%dir %{tomcat_temp_dir}
%{tomcat_home_dir}/temp

%dir %{tomcat_work_dir}
%{tomcat_home_dir}/work

%dir %{tomcat_webapps_dir}
%{tomcat_home_dir}/webapps

%dir %{tomcat_logs_dir}
%{tomcat_home_dir}/logs

%dir %{tomcat_conf_dir}
%config(noreplace) %{tomcat_conf_dir}/catalina.policy
%config(noreplace) %{tomcat_conf_dir}/catalina.properties
%config(noreplace) %{tomcat_conf_dir}/context.xml
%config(noreplace) %{tomcat_conf_dir}/logging.properties
%config(noreplace) %{tomcat_conf_dir}/server.xml
%config(noreplace) %{tomcat_conf_dir}/web.xml
%config(noreplace) %{tomcat_conf_dir}/tomcat-users.xml
%{tomcat_home_dir}/conf

%config(noreplace) %{sysconfig_dir}/tomcat7

%attr(0755,root,root) %{_initddir}/%{servicename}

%attr(0755,root,root) %{_sbindir}/jsvc
