import yaml
import commonmark
from html import escape


TEXT_MARKDOWN = 'text/markdown'
TEXT_HTML = 'text/html'
TEXT_XML = 'text/xml'

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
