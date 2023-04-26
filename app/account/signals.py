from django import dispatch


signin_fail = dispatch.Signal()
signin_success = dispatch.Signal()
