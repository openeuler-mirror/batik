%global classpath batik:rhino:xml-commons-apis:xml-commons-apis-ext:xmlgraphics-commons:jai_imageio
Name:           batik
Version:        1.10
Release:        5
Summary:        Batik is an inline templating engine for CoffeeScript
License:        Apache-2.0 and W3C and MPL-1.1 and GPL-2.0-or-later and Apache-1.1
URL:            https://xmlgraphics.apache.org/batik/
Source0:        http://archive.apache.org/dist/xmlgraphics/batik/source/batik-src-%{version}.zip
Source1:        %{name}-security.policy

Patch1:         0001-Fix-imageio-codec-lookup.patch
Patch6000:      CVE-2019-17566.patch
Patch6001:      CVE-2020-11987.patch

BuildArch:      noarch

BuildRequires:  maven-local junit apache-parent rhino maven-assembly-plugin
BuildRequires:  jython xalan-j2 xml-commons-apis maven-plugin-bundle xmlgraphics-commons

Recommends:     jai-imageio-core	

Provides:       %{name}-css = %{version}-%{release}
Obsoletes:      %{name}-css < 1.8-0.17.svn1230816
Provides:       %{name}-squiggle = %{version}-%{release}
Obsoletes:      %{name}-squiggle < %{version}-%{release}
Provides:       %{name}-svgpp = %{version}-%{release}
Obsoletes:      %{name}-svgpp < %{version}-%{release}
Provides:       %{name}-ttf2svg = %{version}-%{release}
Obsoletes:      %{name}-ttf2svg < %{version}-%{release}
Provides:       %{name}-rasterizer = %{version}-%{release}
Obsoletes:      %{name}-rasterizer < %{version}-%{release}
Provides:       %{name}-slideshow = %{version}-%{release}
Obsoletes:      %{name}-slideshow < %{version}-%{release}
Provides:       %{name}-javadoc = %{version}-%{release}
Obsoletes:      %{name}-javadoc < %{version}-%{release}
Provides:       %{name}-demo = %{version}-%{release}
Obsoletes:      %{name}-demo < %{version}-%{release}

%description
Batik is an inline templating engine for CoffeeScript, inspired by CoffeeKup, 
that lets you write your template directly as a CoffeeScript function.

%package_help

%prep
%autosetup -n %{name}-%{version} -p1

find -name '*.class' -exec rm -f '{}' \;
find -name '*.jar' -exec rm -f '{}' \;

install -p %{SOURCE1} \
	batik-svgrasterizer/src/main/resources/org/apache/batik/apps/rasterizer/resources/rasterizer.policy
install -p %{SOURCE1} \
	batik-svgbrowser/src/main/resources/org/apache/batik/apps/svgbrowser/resources/svgbrowser.policy

%{_bindir}/python3 %{_datadir}/java-utils/pom_editor.py pom_xpath_inject \
	pom:dependency '<optional>true</optional>' batik-all
%{_bindir}/python3 %{_datadir}/java-utils/pom_editor.py pom_xpath_inject \
	'pom:dependency[pom:artifactId="xmlgraphics-commons"]' '<optional>true</optional>' batik-css

cp -a batik-i18n/src/main/java/org/apache/batik/i18n batik-util/src/main/java/org/apache/batik/

%{_bindir}/python3 %{_datadir}/java-utils/pom_editor.py pom_remove_dep :batik-i18n batik-util

for pom in `find -mindepth 2 -name pom.xml -not -path ./batik-all/pom.xml`; do
    %{_bindir}/python3 %{_datadir}/java-utils/pom_editor.py pom_add_plugin org.apache.felix:maven-bundle-plugin \
    $pom "
        <extensions>true</extensions>
        <configuration>
            <instructions>
                <Bundle-SymbolicName>org.apache.batik.$(sed 's:./batik-::;s:/pom.xml::' <<< $pom)</Bundle-SymbolicName>
            </instructions>
        </configuration>
    "
    %{_bindir}/python3 %{_datadir}/java-utils/pom_editor.py pom_xpath_inject pom:project \
	'<packaging>bundle</packaging>' $pom
done

%{_bindir}/python3 %{_datadir}/java-utils/pom_editor.py pom_xpath_set pom:Bundle-SymbolicName \
	org.apache.batik.util.gui batik-gui-util
%{_bindir}/python3 %{_datadir}/java-utils/pom_editor.py pom_disable_module batik-test-old

%{_bindir}/python3 %{_datadir}/java-utils/mvn_package.py :batik-squiggle squiggle
%{_bindir}/python3 %{_datadir}/java-utils/mvn_package.py :batik-squiggle-ext squiggle
%{_bindir}/python3 %{_datadir}/java-utils/mvn_package.py :batik-svgpp svgpp
%{_bindir}/python3 %{_datadir}/java-utils/mvn_package.py :batik-ttf2svg ttf2svg
%{_bindir}/python3 %{_datadir}/java-utils/mvn_package.py :batik-rasterizer rasterizer
%{_bindir}/python3 %{_datadir}/java-utils/mvn_package.py :batik-rasterizer-ext rasterizer
%{_bindir}/python3 %{_datadir}/java-utils/mvn_package.py :batik-slideshow slideshow
%{_bindir}/python3 %{_datadir}/java-utils/mvn_package.py :batik-css css
%{_bindir}/python3 %{_datadir}/java-utils/mvn_package.py ':batik-test*' __noinstall

%{_bindir}/python3 %{_datadir}/java-utils/mvn_file.py :batik-all batik-all

%build
%{_bindir}/python3 %{_datadir}/java-utils/mvn_build.py

%install
%mvn_install

%jpackage_script org.apache.batik.apps.svgbrowser.Main '' '' %{classpath} squiggle true
%jpackage_script org.apache.batik.apps.svgpp.Main '' '' %{classpath} svgpp true
%jpackage_script org.apache.batik.apps.ttf2svg.Main '' '' %{classpath} ttf2svg true
%jpackage_script org.apache.batik.apps.rasterizer.Main '' '' %{classpath} rasterizer true
%jpackage_script org.apache.batik.apps.slideshow.Main '' '' %{classpath} slideshow true

install -d %{buildroot}/%{_datadir}/%{name}/
cp -a samples %{buildroot}/%{_datadir}/%{name}/

%files
%defattr(-,root,root)
%license LICENSE
%{_bindir}/*
%{_datadir}/java/*
%{_datadir}/javadoc/*
%{_datadir}/maven-poms/*
%{_datadir}/maven-metadata/*
%{_datadir}/%{name}/samples

%files     help
%defattr(-,root,root)
%doc CHANGES MAINTAIN README NOTICE

%changelog
* Thu Mar 11 2021 wangyue <wangyue92@huawei.com> - 1.10-5
- fix CVE-2020-11987

* Mon Dec 07 2020 zhanghua <zhanghua40@huawei.com> - 1.10-4
- fix CVE-2019-17566

* Tue Dec 10 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.10-3
- Package init
