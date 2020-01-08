import yaml
import commonmark
from html import escape


TEXT_MARKDOWN = 'text/markdown'
TEXT_HTML = 'text/html'
TEXT_XML = 'text/xml'

def cypher_quote(value):
   return value.replace("'",r"\'")

class Article:
   def __init__(self,source,baseuri=None):
      self.baseuri = baseuri
      self.metadata = yaml.load(source,Loader=yaml.Loader)

      self.update()

   def update(self):

      summary = ''
      title = None
      markdown = self.metadata.get('format',TEXT_MARKDOWN)==TEXT_MARKDOWN
      for part in self.metadata.get('content','').split('\n'):
         if markdown and part[0:2]=='# ':
            title = part[2:]
            continue
         if len(part)>0:
            summary = part
            break

      if 'title' not in self.metadata:
         self.metadata['title'] = title

      self.hasTitle = title is not None

      if 'description' not in self.metadata:
         self.metadata['description'] = summary.replace('\n',' ')

      if 'updated' not in self.metadata:
         self.metadata['updated'] = now()

      if 'published' not in self.metadata:
         self.metadata['published'] = metadata['updated']

   def generateProperties(self,resource=None):
      if resource is None:
         resource = self.metadata.get('id')

      if resource is None:
         resource = ''

      properties = self.metadata.copy()

      if 'id' not in properties:
         properties['id'] = resource
      properties['resource'] = resource

      if 'description' not in properties:
         properties['description'] = ''

      if 'genre' not in properties:
         properties['genre'] = 'blog'

      for name in ['published','updated']:
         dt = properties.get(name)
         if dt is not None and type(dt)!=str:
            properties[name] = dt.isoformat()
      return properties

   def toHTML(self,html,generateTitle=False,resource=None):

      properties = self.generateProperties(resource=resource)

      for name in properties.keys():
         value = properties[name]
         if type(value)==str:
            if name=='resource':
               properties[name] = escape(value,quote=True)
            else:
               properties[name] = escape(value)
      properties['keywords'] = ','.join(['"' + m + '"' for m in properties.get('keywords',[])])

      html.write("""<article xmlns="http://www.w3.org/1999/xhtml" vocab="http://schema.org/" typeof="BlogPosting" resource="{resource}">
<script type="application/json+ld">
{{
"@context" : "http://schema.org/",
"@id" : "{id}",
"genre" : "{genre}",
"headline" : "{title}",
"description" : "{description}",
"datePublished" : "{published}",
"dateModified" : "{updated}",
"keywords" : [{keywords}]""".format(**properties))
      if 'author' in properties:
         html.write(',\n"author" : [ ')
         authors = properties.get('author',[])
         for index,author in enumerate(authors if type(authors)==list else [authors]):
            if (index>0):
               html.write(', ')
            html.write('{{ "@type" : "Person", "name" : "{}" }}'.format(author))
         html.write(']')
      html.write("""
}
</script>
""")

      if generateTitle and not self.hasTitle:
         html.write("<h1>{}</h1>".format(properties['title']))

      format = properties.get('format',TEXT_MARKDOWN)
      if 'content' in properties:
         self.transformContent(properties['content'],format,TEXT_HTML,html)

      html.write('</article>\n')

   def transformContent(self,content,fromType,targetType,output):
      if fromType==TEXT_MARKDOWN and targetType==TEXT_HTML:
         output.write(commonmark.commonmark(content))
      elif fromType==TEXT_HTML and targetType==TEXT_HTML:
         output.write(content)
      else:
         raise ValueError('Unable to convert {fromType} to {targetType}'.format(fromType=fromType,targetType=targetType))


   def toTurtle(self,triples,resource='',source=None):

      properties = self.generateProperties(resource=resource)

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
      triples.write(' .\n')

   def toCypher(self,cypher,resource='',source=None,useMerge=True):
      properties = self.generateProperties(resource=resource)

      for name in properties.keys():
         value = properties[name]
         if type(value)==str:
            properties[name] = cypher_quote(value)

      if useMerge:
         self.toCypherMerge(cypher,properties,source=source)
      else:
         self.toCypherCreate(cypher,properties,source=source)

   def toCypherMerge(self,cypher,properties,source=None):

      cypher.write("""
MERGE (n:Article {{id:'{id}'}})
SET n.genre = '{genre}',
    n.headline = '{title}',
    n.description = '{description}',
    n.datePublished = '{published}',
    n.dateModified = '{updated}',
    n.url = '{resource}'
""".format(**properties))

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

   def toCypherCreate(self,cypher,properties,source=None):

      cypher.write("""
CREATE (n:Article {{id:'{id}'}})
SET n.genre = '{genre}',
    n.headline = '{title}',
    n.description = '{description}',
    n.datePublished = '{published}',
    n.dateModified = '{updated}',
    n.url = '{resource}'
""".format(**properties))

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
