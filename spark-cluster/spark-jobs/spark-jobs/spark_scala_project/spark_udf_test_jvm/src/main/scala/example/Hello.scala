package com.scala_custom_udfs.udfs

import org.apache.spark.sql.SparkSessionExtensions
import org.apache.spark.sql.catalyst.expressions._
import org.apache.spark.sql.catalyst.expressions.codegen.{CodegenContext, ExprCode}
import org.apache.spark.sql.catalyst.expressions.ExpressionDescription
import org.apache.spark.sql.types.{DataType, StringType}
import org.apache.spark.unsafe.types.UTF8String

// Custom Catalyst Expression
@ExpressionDescription(
  usage = "_FUNC_(str) - Reverses the input string",
  examples = """
    Examples:
      > SELECT reverse_str("abc");
       cba
  """,
  since = "1.0"
)
case class ReverseStr(child: Expression) extends UnaryExpression {

  override def dataType: DataType = StringType
  override def nullable: Boolean = true
  override def prettyName: String = "reverse_str"

  // Actual JVM evaluation
  override protected def nullSafeEval(input: Any): Any =
    input.asInstanceOf[UTF8String].reverse()

  // Required by UnaryExpression
  override protected def withNewChildInternal(newChild: Expression): Expression =
    copy(child = newChild)

  // Required for code generation
  override protected def doGenCode(ctx: CodegenContext, ev: ExprCode): ExprCode =
    defineCodeGen(ctx, ev, c => s"$c.reverse()")
}

// Extension injector
class CustomExtensions extends (SparkSessionExtensions => Unit) {
  def apply(e: SparkSessionExtensions): Unit = {
    e.injectFunction(
      (
        org.apache.spark.sql.catalyst.FunctionIdentifier("reverse_str"),
        new ExpressionInfo(classOf[ReverseStr].getName, "reverse_str"),
        (exprs: Seq[Expression]) => ReverseStr(exprs.head)
      )
    )
  }
}
