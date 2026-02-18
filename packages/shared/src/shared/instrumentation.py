from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def instrument_app(app, service_name: str):
    resource = Resource.create(attributes={"service.name": service_name})

    # Configure Tracer Provider
    provider = TracerProvider(resource=resource)

    # Configure OTLP Exporter (Jaeger)
    # 4317 is the default OTLP gRPC port
    exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)

    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

    # Automatic FastAPI Instrumentation
    FastAPIInstrumentor.instrument_app(app)
