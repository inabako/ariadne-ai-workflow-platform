# Retry And Reconnect

Retry is limited to errors that are safe to repeat, such as timeout before execution or connection loss before a request is accepted.

Do not automatically retry a tool call when the server may have completed the operation.

