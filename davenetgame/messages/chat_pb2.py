# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chat.proto

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
  name='chat.proto',
  package='',
  syntax='proto2',
  serialized_pb=_b('\n\nchat.proto\"A\n\x04\x43hat\x12\n\n\x02id\x18\x01 \x02(\x07\x12\r\n\x05mtype\x18\x02 \x02(\x07\x12\x11\n\ttimestamp\x18\x03 \x02(\x01\x12\x0b\n\x03msg\x18\x04 \x01(\t')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_CHAT = _descriptor.Descriptor(
  name='Chat',
  full_name='Chat',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Chat.id', index=0,
      number=1, type=7, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mtype', full_name='Chat.mtype', index=1,
      number=2, type=7, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='Chat.timestamp', index=2,
      number=3, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='msg', full_name='Chat.msg', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=14,
  serialized_end=79,
)

DESCRIPTOR.message_types_by_name['Chat'] = _CHAT

Chat = _reflection.GeneratedProtocolMessageType('Chat', (_message.Message,), dict(
  DESCRIPTOR = _CHAT,
  __module__ = 'chat_pb2'
  # @@protoc_insertion_point(class_scope:Chat)
  ))
_sym_db.RegisterMessage(Chat)


# @@protoc_insertion_point(module_scope)
