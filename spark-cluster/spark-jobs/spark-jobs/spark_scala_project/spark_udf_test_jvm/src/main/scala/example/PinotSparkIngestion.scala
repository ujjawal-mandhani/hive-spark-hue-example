package com.custom_pinot_ingestion.test

import org.apache.pinot.spi.ingestion.batch.IngestionJobLauncher
import org.apache.pinot.spi.ingestion.batch.spec.SegmentGenerationJobSpec
import org.apache.pinot.spi.utils.GroovyTemplateUtils
import org.apache.spark.sql.SparkSession
import org.apache.spark.SparkFiles
import java.nio.file.{Files, Paths}
import java.nio.charset.StandardCharsets
import java.net.{HttpURLConnection, URL}
import scala.jdk.CollectionConverters._
import java.io.{File, FileInputStream, BufferedInputStream}
import org.apache.http.client.methods.HttpPost
import org.apache.http.entity.mime.MultipartEntityBuilder
import org.apache.http.impl.client.HttpClients
import org.apache.http.HttpHeaders


object PinotSparkIngestion {

  def createSchemaWithBearer(
      controllerUrl: String,
      schemaPath: String,
      token: String
  ): Unit = {

    val schemaJson =
      new String(Files.readAllBytes(Paths.get(schemaPath)), StandardCharsets.UTF_8)

    val url = new URL(s"$controllerUrl/schemas")
    val conn = url.openConnection().asInstanceOf[HttpURLConnection]

    conn.setRequestMethod("POST")
    conn.setRequestProperty("Content-Type", "application/json")
    conn.setRequestProperty("Authorization", s"Basic $token")
    conn.setDoOutput(true)

    val os = conn.getOutputStream
    os.write(schemaJson.getBytes(StandardCharsets.UTF_8))
    os.close()

    val code = conn.getResponseCode
    if (code != 200 && code != 201) {
      val err =
        Option(conn.getErrorStream).map(scala.io.Source.fromInputStream(_).mkString).getOrElse("")
      throw new RuntimeException(s"Schema creation failed ($code): $err")
    }

    conn.disconnect()
  }

  def createTableWithBasicAuth(
    controllerUrl: String,
    tablePath: String,
    token: String
  ): Unit = {
    val payload = new String(
      Files.readAllBytes(Paths.get(tablePath)),
      StandardCharsets.UTF_8
    )

    val url = new URL(s"$controllerUrl/tables")
    val conn = url.openConnection().asInstanceOf[HttpURLConnection]

    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setRequestProperty("Content-Type", "application/json")
    conn.setRequestProperty("Authorization", s"Basic $token")

    conn.getOutputStream.write(payload.getBytes(StandardCharsets.UTF_8))

    val code = conn.getResponseCode
    if (code != 200) {
      val err = scala.io.Source.fromInputStream(conn.getErrorStream).mkString
      throw new RuntimeException(s"Table creation failed ($code): $err")
    }

    println("✅ Pinot table created successfully")
  }

  def pushSegmentWithAuth(controllerUrl: String, tableName: String, segmentFile: File, token: String): Unit = {
    val httpClient = HttpClients.createDefault()
    try {
      val uploadUrl = s"$controllerUrl/v2/segments?tableName=$tableName&tableType=OFFLINE"
      val httpPost = new HttpPost(uploadUrl)
      
      // Add auth header
      httpPost.setHeader(HttpHeaders.AUTHORIZATION, s"Basic $token")
      
      // Build multipart entity with segment file
      val builder = MultipartEntityBuilder.create()
      builder.addBinaryBody("segment", segmentFile)
      httpPost.setEntity(builder.build())
      
      val response = httpClient.execute(httpPost)
      val statusCode = response.getStatusLine.getStatusCode
      
      if (statusCode != 200) {
        val entity = response.getEntity
        val responseBody = if (entity != null) scala.io.Source.fromInputStream(entity.getContent).mkString else ""
        throw new RuntimeException(s"Segment push failed ($statusCode): $responseBody")
      }
      
      println(s"✅ Successfully pushed segment: ${segmentFile.getName}")
    } finally {
      httpClient.close()
    }
  }


  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Pinot Spark Ingestion")
      .master("local[*]") // can also read from --master flag
      .getOrCreate()
    val jobSpecFilePath = SparkFiles.get("jobSpec.yaml")
    val schemaPath = SparkFiles.get("organisation_data.json")
    val tablePath = SparkFiles.get("organisation_table.json")
    val conf = spark.sparkContext.getConf
    val token = conf.get("spark.pinot.auth.token")
    val controllerUrl = "http://host.docker.internal:54882"
    createSchemaWithBearer(controllerUrl, schemaPath, token)
    createTableWithBasicAuth(controllerUrl, tablePath, token)
    // Files.copy(
    //   Paths.get(src),
    //   dst,
    //   java.nio.file.StandardCopyOption.REPLACE_EXISTIN
    // )
    // val jobSpecFilePath = "jobSpec.yaml"
    Thread.sleep(5000)
    val outputDir = "/tmp/pinot-segments"
    val values = List(
      "TABLENAME=organisation_data_OFFLINE",
      "inputDirURI=hdfs://namenode:8020/user/airflow/organisation/",
      s"outputDirURI=file://$outputDir",
      // "schemaURI=http://host.docker.internal:54882/schemas/organisation_data",
      // "tableConfigURI=http://host.docker.internal:54882/tables/organisation_data_OFFLINE",
      "schemaURI=file://" + schemaPath,
      "tableConfigURI=file://" + tablePath,
      "push_controller_auth_token=Basic YWRtaW46dmVyeXNlY3JldA"
    )
    values.foreach(println)
    val env = Map.empty[String, String]
    System.setProperty("http.auth.header", "Basic YWRtaW46dmVyeXNlY3JldA")
    // val env = Map(
    //   "PINOT_CONTROLLER_AUTH_TOKEN" ->
    //     "Authorization=Basic YWRtaW46dmVyeXNlY3JldA"
    // )
    // System.setProperty(
    //   "pinot.controller.http.headers",
    //   "Authorization=Basic YWRtaW46dmVyeXNlY3JldA"
    // )
    val spec: SegmentGenerationJobSpec =
      IngestionJobLauncher.getSegmentGenerationJobSpec(
        jobSpecFilePath,
        null,
        GroovyTemplateUtils.getTemplateContext(values.asJava),
        // env.asJava
        null
      )
    spec.setJobType("SegmentCreation")  
    IngestionJobLauncher.runIngestionJob(spec)
    val outputDirFile = new File(outputDir)
    val segmentFiles = outputDirFile.listFiles().filter(_.getName.endsWith(".tar.gz"))
    
    segmentFiles.foreach { segmentFile =>
      println(s"Pushing segment: ${segmentFile.getAbsolutePath}")
      pushSegmentWithAuth(controllerUrl, "organisation_data_OFFLINE", segmentFile, token)
    }
  }
}
