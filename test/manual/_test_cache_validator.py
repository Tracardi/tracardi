# # Example usage:
# from tracardi.context import ServerContext, Context
#
#
# # from tracardi.context import ServerContext, Context
# def my_function():
#     print("Executing my_function...")
#     # Simulating some logic
#     return "Success!"
#
#
# # Test the decorators
# if __name__ == "__main__":
#     with ServerContext(Context(production=False)):
#         with invalidate_cache_on_update(database="my_db", table="my_table"):
#             print(my_function())  # Should execute successfully and trigger table_changed