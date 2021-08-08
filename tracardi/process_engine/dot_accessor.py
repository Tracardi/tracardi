# todo remove after 01-09-2021
# from dotty_dict import dotty
# from tracardi.domain.event import Event
# from tracardi.domain.flow import Flow
# from tracardi.domain.profile import Profile
# from tracardi.domain.session import Session
#
#
# class DotAccessor:
#
#     def __init__(self, profile: Profile, session: Session, payload: dict, event: Event, flow: Flow):
#         self.flow = dotty(flow.dict())
#         self.event = dotty(event.dict())
#         self.payload = dotty(payload)
#         self.session = dotty(session.dict())
#         self.profile = dotty(profile.dict())
#
#     def __delitem__(self, key):
#         if key.startswith('profile@'):
#             key = key[len('profile@'):]
#             del self.profile[key]
#         elif key.startswith('session@'):
#             raise KeyError("Could not set session, session is read only")
#         elif key.startswith('flow@'):
#             raise KeyError("Could not set flow, flow is read only")
#         elif key.startswith('payload@'):
#             key = key[len('payload@'):]
#             del self.payload[key]
#         elif key.startswith('event@'):
#             raise KeyError("Could not delete event, event is read only")
#         else:
#             raise ValueError(
#                 "Invalid dot notation. Accessor not available. " +
#                 "Please start dotted path with one of the accessors: [profile@, session@, payload@, event@] ")
#
#     def __setitem__(self, key, value):
#         if key.startswith('profile@'):
#             key = key[len('profile@'):]
#             self.profile[key] = self.__getitem__(value) if not isinstance(value, dict) else value
#         elif key.startswith('session@'):
#             raise KeyError("Could not set session, session is read only")
#         elif key.startswith('flow@'):
#             raise KeyError("Could not set flow, flow is read only")
#         elif key.startswith('payload@'):
#             key = key[len('payload@'):]
#             self.payload[key] = self.__getitem__(value) if not isinstance(value, dict) else value
#         elif key.startswith('event@'):
#             raise KeyError("Could not set event, event is read only")
#         else:
#             raise ValueError(
#                 "Invalid dot notation. Accessor not available. " +
#                 "Please start dotted path with one of the accessors: [profile@, session@, payload@, event@] ")
#
#     def __getitem__(self, dot_notation):
#         if isinstance(dot_notation, str):
#             if dot_notation.startswith('flow@'):
#                 value = dot_notation[len('flow@'):]
#                 try:
#                     return self.flow[value]
#                 except KeyError:
#                     raise KeyError("Invalid dot notation. Could not find value for `{}` in flow.".format(value))
#             elif dot_notation.startswith('profile@'):
#                 value = dot_notation[len('profile@'):]
#                 try:
#                     return self.profile[value]
#                 except KeyError:
#                     raise KeyError("Invalid dot notation. Could not find value for `{}` in profile.".format(value))
#             elif dot_notation.startswith('session@'):
#                 value = dot_notation[len('session@'):]
#                 try:
#                     return self.session[value]
#                 except KeyError:
#                     raise KeyError("Invalid dot notation. Could not find value for `{}` in session.".format(value))
#             elif dot_notation.startswith('payload@'):
#                 value = dot_notation[len('payload@'):]
#                 try:
#                     return self.payload[value]
#                 except KeyError:
#                     raise KeyError("Invalid dot notation. Could not find value for `{}` in payload.".format(value))
#             elif dot_notation.startswith('event@'):
#                 value = dot_notation[len('event@'):]
#                 try:
#                     return self.event[value]
#                 except KeyError:
#                     raise KeyError("Invalid dot notation. Could not find value for `{}` in event.".format(value))
#         return dot_notation
#
#     def __contains__(self, item):
#         try:
#             self.__getitem__(item)
#             return True
#         except KeyError:
#             return False
#
#     @staticmethod
#     def get(dot_notation, payload, prefix):
#         value = dot_notation[len(prefix + '@'):]
#         try:
#             return payload[value]
#         except KeyError:
#             raise KeyError("Could not find value for `{}` in {}".format(value, prefix))
#
#     @staticmethod
#     def set(key, value, payload, prefix):
#         key = key[len(prefix + '@'):]
#         payload[key] = value
