def pokegrabber(pokemon=''):
    import requests
    if pokemon == 'random' or pokemon == '':
        from random import randint
        pokemon = randint(1,1025)
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon}'
    response = requests.get(url)
    if response.ok:
        data = response.json()
        pokedict = {
            'name': data['forms'][0]['name'],
            'ability1': data['abilities'][0],
            'base_exp': data['base_experience'],
            'sprite_url': data['sprites']['other']['official-artwork']['front_default']
        }
        return pokedict
    elif response.status_code == 404: return '404 error code. Pokemon name or ID either doesn\'t exist or was mispelled. Please try again.'
    else: return f'{response.status_code} error code.'

print(pokegrabber(''))