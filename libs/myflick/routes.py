from werkzeug.routing import Map, Rule, EndpointPrefix

routes = [
    EndpointPrefix('index|', [
        Rule('/', endpoint='index')]),
    EndpointPrefix('login|', [
        Rule('/login/g', defaults = {'original_url': ''}, endpoint = 'g_request', methods = ['GET']),
        Rule('/login/g/<path:original_url>', endpoint = 'g_request', methods = ['GET']),
        Rule('/login/callback/g', endpoint = 'g_callback', methods = ['GET']),
        Rule('/login/twitter', defaults = {'original_url': ''}, endpoint = 'twitter_request', methods = ['GET']),
        Rule('/login/twitter/<path:original_url>', endpoint = 'twitter_request', methods = ['GET']),
        Rule('/login/callback/twitter', defaults = {'original_url': ''}, endpoint = 'twitter_callback', methods = ['GET']),
        Rule('/login/callback/twitter/<path:original_url>', endpoint = 'twitter_callback', methods = ['GET']),
        Rule('/login/fb', defaults = {'original_url': ''}, endpoint = 'fb_request', methods = ['GET']),
        Rule('/login/fb/<path:original_url>', endpoint = 'fb_request', methods = ['GET']),
        Rule('/login/callback/fb', defaults = {'original_url': ''}, endpoint = 'fb_callback', methods = ['GET']),
        Rule('/login/callback/fb/<path:original_url>', endpoint = 'fb_callback', methods = ['GET']),
        Rule('/login/logout', defaults = {'original_url': ''}, endpoint = 'logout', methods = ['GET']),
        Rule('/login/logout/<path:original_url>', endpoint='logout', methods=['GET'])]),
    EndpointPrefix('mgmt|', [
        Rule('/mgmt/update/movies', endpoint='update_movies', methods=['GET'])]),
    EndpointPrefix('search|', [
        Rule('/autocomplete/movie/<path:q>', endpoint='auto_movie', methods=['GET'])]),
    EndpointPrefix('rating|', [
        Rule('/user/rate', endpoint='user_rate', methods=['POST'])]),
    EndpointPrefix('movie|', [
        Rule('/movie/partial/<int:movie_id>', endpoint='partial', methods=['GET']),
        Rule('/movie/<int:movie_id>-<path:dummy>', endpoint='show', methods=['GET']),
        Rule('/movie/missing', endpoint='missing', methods=['GET']),
        Rule('/movie/missing', endpoint='fill_missing', methods=['POST'])]),
    EndpointPrefix('user|', [
        Rule('/user/<int:user_id>-<path:dummy>', endpoint='show', methods=['GET']),
        Rule('/home', endpoint='home', methods=['GET'])]),
    EndpointPrefix('cast|', [
        Rule('/director/<path:fullname>', defaults = {'crew': 'director'}, endpoint='show', methods=['GET']),
        Rule('/screenwriter/<path:fullname>', defaults = {'crew': 'screenwriter'}, endpoint='show', methods=['GET']),
        Rule('/actor/<path:fullname>', defaults = {'crew': 'actor'}, endpoint='show', methods=['GET'])])
]

url_map = Map(routes, strict_slashes = False)
