from behave import *


@given("we have a user")
def step_impl(context):
    raise NotImplementedError(u'STEP: Given we have a user')


@when("a user requests discover")
def step_impl(context):
    raise NotImplementedError(u'STEP: When a user requests discover')


@then("a list of movies will be returned")
def step_impl(context):
    raise NotImplementedError(u'STEP: Then a list of movies will be returned')


@then("the movies in the releases section are released recently")
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the movies in the releases section are released recently')


@then("the movies in the popular section are released recently")
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the movies in the popular section are released recently')


@when('a user requests the movie with id "{movie_id}"')
def step_impl(context, movie_id):
    raise NotImplementedError(u'STEP: When a user requests the movie with id "1234"')


@then("movie details will be returned")
def step_impl(context):
    raise NotImplementedError(u'STEP: Then movie details will be returned')


@given('A movie with id "{movie_id}" is reviewed')
def step_impl(context, movie_id):
    raise NotImplementedError(u'STEP: Given A movie with id "1234" is reviewed')


@when('When a user requests the movie with id "{movie_id}"')
def step_impl(context, movie_id):
    raise NotImplementedError(u'STEP: When When a user requests the movie with id "1234"')


@then("the review will be returned")
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the review will be returned')


@given('A movie is added to the watchlist "{movie_id}"')
def step_impl(context, movie_id):
    raise NotImplementedError(u'STEP: Given A movie is added to the watchlist "id"')


@when('a user requests the watchlist "{movie_id}"')
def step_impl(context, movie_id):
    raise NotImplementedError(u'STEP: When a user requests the watchlist "id"')


@then("the added movie can is on the watchlist")
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the added movie can is on the watchlist')