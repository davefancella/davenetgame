# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ack.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='ack.proto',
  package='',
  syntax='proto2',
  serialized_pb=_b('\n\tack.proto\"D\n\x03\x41\x63k\x12\n\n\x02id\x18\x01 \x02(\x07\x12\r\n\x05mtype\x18\x02 \x02(\x07\x12\x11\n\ttimestamp\x18\x03 \x02(\x01\x12\x0f\n\x07replied\x18\x04 \x03(\r')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_ACK = _descriptor.Descriptor(
  name='Ack',
  full_name='Ack',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Ack.id', index=0,
      number=1, type=7, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mtype', full_name='Ack.mtype', index=1,
      number=2, type=7, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='Ack.timestamp', index=2,
      number=3, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='replied', full_name='Ack.replied', index=3,
      number=4, type=13, cpp_type=3, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=13,
  serialized_end=81,
)

DESCRIPTOR.message_types_by_name['Ack'] = _ACK

Ack = _reflection.GeneratedProtocolMessageType('Ack', (_message.Message,), dict(
  DESCRIPTOR = _ACK,
  __module__ = 'ack_pb2'
  # @@protoc_insertion_point(class_scope:Ack)
  ))
_sym_db.RegisterMessage(Ack)


# @@protoc_insertion_point(module_scope)