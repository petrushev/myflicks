from werkzeug.routing import Map, Rule, EndpointPrefix

routes = [
    EndpointPrefix('index|', [
        Rule('/', endpoint='index')]),
    EndpointPrefix('login|', [
        Rule('/login/g', defaults = {'original_url': ''}, endpoint = 'g_request', methods = ['GET']),
        Rule('/login/g/<path:original_url>', endpoint = 'g_request', methods = ['GET']),
        Rule('/login/callback/g', endpoint = 'g_callback', methods = ['GET']),
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
        Rule('/movie/<int:movie_id>-<path:dummy>', endpoint='show', methods=['GET'])]),
    EndpointPrefix('user|', [
        Rule('/user/<int:user_id>-<path:dummy>', endpoint='show', methods=['GET']),
        Rule('/home', endpoint='home', methods=['GET'])])
]

url_map = Map(routes, strict_slashes = False)
