import Dependencies._
import sbtassembly.AssemblyPlugin.autoImport._
ThisBuild / scalaVersion     := "2.13.14"
ThisBuild / version          := "0.1.0-SNAPSHOT"
ThisBuild / organization     := "com.example"
ThisBuild / organizationName := "example"

lazy val root = (project in file("."))
  .settings(
    name := "spark_udf_test_jvm",
    resolvers ++= Seq(
      "Confluent" at "https://packages.confluent.io/maven/",
      // "Apache Releases" at "https://repository.apache.org/content/repositories/releases/",
      // "Apache Snapshots" at "https://repository.apache.org/content/repositories/snapshots/",
      "Maven Central" at "https://repo1.maven.org/maven2/"
    ),
    libraryDependencies ++= Seq(
      "org.apache.spark" %% "spark-core" % "4.0.1" % "provided",
      "org.apache.spark" %% "spark-sql"  % "4.0.1" % "provided",
      // "org.scalatest" %% "scalatest" % "3.2.16" % Test,
      // "org.apache.pinot" % "pinot" % "1.4.0",
      // "org.apache.pinot" % "pinot-distribution" % "1.4.0",
      // "org.apache.pinot" % "pinot-plugins" % "1.4.0",
      // "org.apache.pinot" % "pinot-core" % "1.4.0",
      // "org.apache.pinot" % "pinot-tools" % "1.4.0"
      "org.apache.spark" %% "spark-core" % "4.0.1" % "provided",
      "org.apache.spark" %% "spark-sql"  % "4.0.1" % "provided",
      "org.apache.pinot" % "pinot-spi"    % "1.4.0",
      "org.apache.pinot" % "pinot-common" % "1.4.0",
      "org.apache.pinot" % "pinot-core"   % "1.4.0",
      "org.codehaus.groovy" % "groovy" % "3.0.21",
      "org.apache.pinot" % "pinot-plugins" % "1.4.0",
      "org.apache.httpcomponents" % "httpclient" % "4.5.14",
      "org.apache.httpcomponents" % "httpmime" % "4.5.14"
    ),
    Compile / unmanagedSources := {
      val filesToIgnore = Set("Hello.scala")
      (Compile / unmanagedSources).value.filterNot(file => filesToIgnore.contains(file.getName))
    },
    assembly / assemblyMergeStrategy := {
      case PathList("META-INF", _*) => MergeStrategy.discard
      case _                        => MergeStrategy.first
    }
  )


// Uncomment the following for publishing to Sonatype.
// See https://www.scala-sbt.org/1.x/docs/Using-Sonatype.html for more detail.

// ThisBuild / description := "Some descripiton about your project."
// ThisBuild / licenses    := List("Apache 2" -> new URL("http://www.apache.org/licenses/LICENSE-2.0.txt"))
// ThisBuild / homepage    := Some(url("https://github.com/example/project"))
// ThisBuild / scmInfo := Some(
//   ScmInfo(
//     url("https://github.com/your-account/your-project"),
//     "scm:git@github.com:your-account/your-project.git"
//   )
// )
// ThisBuild / developers := List(
//   Developer(
//     id    = "Your identifier",
//     name  = "Your Name",
//     email = "your@email",
//     url   = url("http://your.url")
//   )
// )
// ThisBuild / pomIncludeRepository := { _ => false }
// ThisBuild / publishTo := {
//   val nexus = "https://oss.sonatype.org/"
//   if (isSnapshot.value) Some("snapshots" at nexus + "content/repositories/snapshots")
//   else Some("releases" at nexus + "service/local/staging/deploy/maven2")
// }
// ThisBuild / publishMavenStyle := true
