from django import template
from ..models import Snippet

register = template.Library()

default_snippet = {
		"default": '"New Snippet"',
		"safe": True,
}

class snippet_node(template.Node):
	def __init__(self, name, default):
		self.name = template.Variable(name)
		self.default = default
	
	def render(self, context):
		name = self.name.resolve(context)
		default = self.default.render(context)
		return Snippet.cache.get(name, default)

@register.tag
def snippet(parser, token):
	args, kwargs = interpret_args(
		token.split_contents(),
		default=default_snippet,
	)
	default = fake_nodelist(kwargs['default'])
	name = args[0]
	return snippet_node(name, default)

@register.tag
def snippetblock(parser, token):
	args, kwargs = interpret_args(
		token.split_contents(),
		default=default_snippet,
	)
	name = args[0]
	default = parser.parse(('endsnippetblock',))
	parser.delete_first_token()
	return snippet_node(name, default)

def interpret_args(token_args, default):
	args = []
	kwargs = dict(default)
	for token in token_args[1:]:
		if '=' in token:
			if token[0] in ('\'', '"'):
				args.append(token)
			else:
				key, value = token.split('=',1)
				if key in kwargs:
					kwargs[key] = value
		else:
			args.append(token)
	if not len(args):
		raise template.TemplateSyntaxError("Snippetblock needs an ID")
	return args, kwargs

class fake_nodelist(object):
	def __init__(self, content):
		self.content = template.Variable(content)
	
	def render(self, context):
		return self.content.resolve(context)
