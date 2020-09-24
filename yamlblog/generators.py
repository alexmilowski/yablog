from io import StringIO
import commonmark
from html import escape

from yamlblog import Article


class Generator:
   def __init__(self):
      pass

   def generate_string(self,article,**kwargs):
      output = StringIO()
      self.generate(article,output,**kwargs)
      return output.getvalue()

   def generate(self,article,targeOutput,**kwargs):
      pass

def quote_escape(value):
   return value.replace('"',r'\"')

class HTMLGenerator(Generator):
   def __init__(self,generate_title=False,generate_info=False):
      self.generate_title = generate_title
      self.generate_info = generate_info

   def generate(self,article,html,**kwargs):
      generate_title = kwargs.get('generate_title',self.generate_title)
      generate_info = kwargs.get('generate_info',self.generate_info)
      resource = kwargs.get('resource')

      properties = article.generate_properties(resource=resource)

      for name in properties.keys():
         value = properties[name]
         if name=='content':
            continue
         if name=='articleBody':
            continue
         if type(value)==str:
            if name=='resource':
               properties[name] = escape(value,quote=True)
            else:
               properties[name] = escape(value,quote=False)
      properties['keywords'] = ','.join(properties.get('keywords',[]))

      ld_properties = properties.copy()
      for name in ['title','description','keywords']:
         ld_properties[name] = quote_escape(ld_properties[name])

      html.write("""<article xmlns="http://www.w3.org/1999/xhtml" vocab="http://schema.org/" typeof="BlogPosting" resource="{resource}">
<script type="application/ld+json">
{{
"@context" : "http://schema.org/",
"@id" : "{id}",
"@type" : "BlogPosting",
"genre" : "{genre}",
"headline" : "{title}",
"description" : "{description}",
"datePublished" : "{published}",
"dateModified" : "{updated}",
"keywords" : "{keywords}" """.format(**ld_properties))
      if 'author' in properties:
         html.write(',\n"author" : [ ')
         authors = properties.get('author',[])
         for index,author in enumerate(authors if type(authors)==list else [authors]):
            if (index>0):
               html.write(', ')
            html.write('{{ "@type" : "Person", "name" : "{}" }}'.format(author))
         html.write(']')
      if 'publisher' in properties:
         publisher = properties['publisher']
         html.write(',\n"publisher" : {')
         sep = ' '
         for name in publisher.keys():
            value = publisher[name]
            html.write(sep+'"{name}" : "{value}"'.format(name=name,value=value))
            sep = ', '
         html.write('}')
      html.write("""
}
</script>
""")
      if generate_title and not article.has_title:
         html.write("<h1 property='headline'>{}</h1>\n".format(properties['title']))

      if generate_info:
         properties['publishedDisplay'] = ' '.join(properties['published'].split('T'))
         html.write('<section class="info">\n')
         html.write('''
<div class="metadata">
<p>
<a href="{id}" title="link to this entry">🔗</a> Published on
<span property="datePublished" content="{published}">{publishedDisplay}</span>
<span property="dateModified" content="{updated}"></span>
</p>
<p property="keywords">{keywords}</p>
<p property="description">{description}</p>
</div>
'''.format(**properties))
         html.write('</p>\n')
         if 'author' in properties:
            authors = properties.get('author',[])
            for index,author in enumerate(authors if type(authors)==list else [authors]):
               html.write('<p property="author" typeof="Person"><span property="name">{name}</span></p>\n'.format(name=author))
         if 'publisher' in properties:
            publisher = properties['publisher']
            for name in publisher.keys():
               value = publisher[name]
               html.write('<p property="publisher" typeof="Organization"><span property="name">{name}</span></p>\n'.format(name=value))
         html.write('</section>\n')


      if 'content' in properties:
         format = properties.get('format',Article.TEXT_MARKDOWN)
         self.transform_content(properties['content'],format,Article.TEXT_HTML,html)

      html.write('</article>\n')

   def transform_content(self,content,fromType,targetType,output):
      if fromType==Article.TEXT_MARKDOWN and targetType==Article.TEXT_HTML:
         output.write(commonmark.commonmark(content))
      elif fromType==Article.TEXT_HTML and targetType==Article.TEXT_HTML:
         output.write(content)
      else:
         raise ValueError('Unable to convert {fromType} to {targetType}'.format(fromType=fromType,targetType=targetType))

class TurtleGenerator(Generator):
   def __init__(self,embed_content=False):
      self.embed_content = embed_content

   def generate(self,article,targetOutput,**kwargs):

      embed_content = kwargs.get('embed_content',self.embed_content)
      resource = kwargs.get('resource')
      source = kwargs.get('source')

      properties = article.generate_properties(resource=resource)

      properties['keywords'] = ','.join(['"' + m + '"' for m in properties.get('keywords',[])])

      triples.write("""
@base <{id}> .
@prefix schema: <http://schema.org/> .
<>
   a schema:BlogPosting ;
   schema:genre "{genre}";
   schema:headline "{title}" ;
   schema:description "{description}" ;
   schema:datePublished "{published}" ;
   schema:dateModified "{updated}" ;
   schema:url <{resource}>;
   schema:keywords {keywords};
""".format(**properties))

      if 'author' in properties:
         authors = properties.get('author',[])
         triples.write('   schema:author ')
         for index,author in enumerate(authors if type(authors)==list else [authors]):
            if (index>0):
               triples.write(', ')
            triples.write('[ a schema:Person; schema:name "{}" ]'.format(author))
      if source is not None:
         triples.write(""";
   schema:associatedMedia [ a schema:MediaObject; schema:contentUrl <{url}>]""".format(url=source))
      if embed_content:
         triples.write(';\n')
         triples.write('   schema:articleBody "{content}"'.format(content=properties['content']))
      triples.write(' .\n')

def cypher_quote(value):
   return value.replace("'",r"\'")

class CypherGenerator(Generator):
   def __init__(self,embed_content=False,use_merge=True):
      self.embed_content = embed_content
      self.use_merge = use_merge

   def generate(self,article,targetOutput,**kwargs):

      embed_content = kwargs.get('embed_content',self.embed_content)
      use_merge = kwargs.get('use_merge',self.use_merge)
      resource = kwargs.get('resource')
      source = kwargs.get('source')

      properties = article.generate_properties(resource=resource)

      for name in properties.keys():
         value = properties[name]
         if type(value)==str:
            properties[name] = cypher_quote(value)

      if use_merge:
         self.generate_merge(targetOutput,properties,source=source,embed_content=embed_content)
      else:
         self.generate_create(targetOutput,properties,source=source,embed_content=embed_content)

   def generate_merge(self,cypher,properties,source=None,embed_content=False):

      cypher.write("""
MERGE (n:Article {{id:'{id}'}})
SET n.genre = '{genre}',
    n.headline = '{title}',
    n.description = '{description}',
    n.datePublished = '{published}',
    n.dateModified = '{updated}',
    n.url = '{resource}'
""".format(**properties))

      if embed_content and 'content' in properties:
         cypher.write("   n.articleBody = '{content}'".format(propertiers.get('content')))

      for index,keyword in enumerate(properties.get('keywords',[])):
         cypher.write("""
MERGE (k{index}:Keyword {{text:'{keyword}'}})
MERGE (n)-[:LabeledWith]->(k{index})""".format(index=index,keyword=keyword))

      authors = properties.get('author',[])
      for index,author in enumerate(authors if type(authors)==list else [authors]):
         cypher.write("""
MERGE (a{index}:Author {{name:'{author}'}})
MERGE (n)-[:AuthoredBy]->(a{index})""".format(index=index,author=author))
      if source is not None:
         cypher.write("""
MERGE (r:Resource {{ url: '{source}'}})
MERGE (n)-[:AssociatedMedia]->(r)""".format(source=source))

   def generate_create(self,cypher,properties,source=None,embed_content=False):

      cypher.write("""
CREATE (n:Article {{id:'{id}'}})
SET n.genre = '{genre}',
    n.headline = '{title}',
    n.description = '{description}',
    n.datePublished = '{published}',
    n.dateModified = '{updated}',
    n.url = '{resource}'
""".format(**properties))

      if embed_content and 'content' in properties:
         cypher.write("   n.articleBody = '{content}'".format(propertiers.get('content')))

      authors = properties.get('author',[])
      for index,keyword in enumerate(properties.get('keywords',[])):
         cypher.write("MERGE (k{index}:Keyword {{text:'{keyword}'}})\n".format(index=index,keyword=keyword))
      for index,author in enumerate(authors if type(authors)==list else [authors]):
         cypher.write("MERGE (a{index}:Author {{name:'{author}'}})\n".format(index=index,author=author))
      cypher.write("WITH n\n")
      for index,keyword in enumerate(properties.get('keywords',[])):
         cypher.write("CREATE (n)-[:LabeledWith]->(k{index})\n".format(index=index,keyword=keyword))
      for index,author in enumerate(authors if type(authors)==list else [authors]):
         cypher.write("CREATE (n)-[:AuthoredBy]->(a{index})\n".format(index=index,author=author))

      if source is not None:
         cypher.write("""
CREATE (r:Resource {{url: '{source}'}})
CREATE (n)-[:AssociatedMedia]->(r)""".format(source=source))

registry = {}

def register_generator(generator,*types):
   for name in types:
      registry[name] = generator

def deregister_generator(*types):
   generators = []
   for name in types:
      r = registry.pop(name,None)
      if r is not None:
         r.append(r)
   return generators

def generator_for(*types):
   for name in types:
      g = registry.get(name)
      if g is not None:
         return g
   return None

def generate(article,type,output,**kwargs):
   g = generator_for(type)
   if g is None:
      raise ValueError('Type {} is not supported.'.format(type))
   g.generate(article,output,**kwargs)

def generate_string(article,type,**kwargs):
   g = generator_for(type)
   if g is None:
      raise ValueError('Type {} is not supported.'.format(type))
   return g.generate_string(article,**kwargs)

register_generator(HTMLGenerator(),'text/html')
register_generator(TurtleGenerator(),'text/turtle')
register_generator(CypherGenerator(),'text/x.cypher')
