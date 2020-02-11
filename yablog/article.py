import yaml

class Publisher:
   def __init__(self,source,baseuri=None):
      self.baseuri = baseuri
      self.metadata = yaml.load(source,Loader=yaml.Loader)

class Article:
   TEXT_MARKDOWN = 'text/markdown'
   TEXT_HTML = 'text/html'
   TEXT_XML = 'text/xml'
   TEXT_TURTLE = 'text/turtle'
   TEXT_CYPHER = 'text/x.cypher'
   def __init__(self,source,baseuri=None,publisher=None):
      self.baseuri = baseuri
      self.metadata = yaml.load(source,Loader=yaml.Loader)
      self.publisher = publisher

      self.update()

   def update(self):

      summary = ''
      title = None
      markdown = self.metadata.get('format',Article.TEXT_MARKDOWN)==Article.TEXT_MARKDOWN
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
         self.metadata['description'] = summary

      if 'updated' not in self.metadata:
         self.metadata['updated'] = now()

      if 'published' not in self.metadata:
         self.metadata['published'] = metadata['updated']

   def generate_properties(self,resource=None):
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

      if self.publisher is not None and 'publisher' not in properties:
         properties['publisher'] = self.publisher.metadata.copy()
      return properties
