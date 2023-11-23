from behave import *


movie_expected_keys = {"id", "poster_url", "backdrop_url", "title", "description", "rating", "release_date"}

@given("we have a user")
def step_impl(context):
    context.user = context.api.user_login("test@test.dk", "1234")
    pass


@when("a user requests discover")
def step_impl(context):
    context.movie_list = context.api.discover_movies()
    pass


@then("a list of movies will be returned")
def step_impl(context):
    assert context.movie_list is not None
    assert len(context.movie_list) > 0
    for i in context.movie_list:
        assert movie_expected_keys.issubset(i)
    raise NotImplementedError(u'STEP: Then a list of movies will be returned')


@then("the movies in the releases section are released recently")
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the movies in the releases section are released recently')


@then("the movies in the popular section are released recently")
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the movies in the popular section are released recently')


@when('a user requests the movie with id "{movie_id}"')
def step_impl(context, movie_id):
    context.movie = context.api.get_movie(movie_id)


@then("movie details will be returned")
def step_impl(context):
    assert context.movie is not None
    assert movie_expected_keys.issubset(context.movie)


@given('A movie with id "{movie_id}" is reviewed')
def step_impl(context, movie_id):
    raise NotImplementedError(u'STEP: Given A movie with id "1234" is reviewed')


@then("the review will be returned")
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the review will be returned')


@given('A movie "{movie_id}" is added to the watchlist "{watch_id}"')
def step_impl(context, movie_id, watch_id):
    context.api.add_movie_to_watchlist(watch_id=watch_id, movie_id=movie_id)
    context.added_movie = movie_id


@when('a user requests the watchlist "{watch_id}"')
def step_impl(context, watch_id):
    context.watchlist = context.api.get_watchlist(watch_id=watch_id)


@then("the added movie is on the watchlist")
def step_impl(context):
    assert context.watchlist is not None
    assert context.added_movies in context.watchlist["movie_ids"]



