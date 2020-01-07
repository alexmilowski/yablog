# yablog

A simple YAML-based blog entry format.

## Motivation

In 2016, I was motivated to make my blog and website easier. I wanted to use "Semantic Web" technology and drive the blog for my website and other content by the "linked data graph". That project is called [duckpond](https://github.com/alexmilowski/duckpond/) and has served me well.

During the process, I wanted a simple authoring format where I could use github to store my blog entries and associated artifacts safely. [Markdown](https://daringfireball.net/projects/markdown/) seemed like a good choice except that I also needed a way to author the metadata. Originally, I settled on a simple header format of key/values. Ultimately, that format has evolved into the use of YAML.

Turns out that Markdown nicely embeds into YAML and so do a lot of other formats. Who knew?

## An Example

Every entry is a set of metadata and content encoded in YAML. The essential metadata map nicely to a [schema.org BlogPosting](http://schema.org/BlogPosting) type although the properties are not named the same. The motivation for the difference in naming is essentially clarity - which is a certainly subjective.

For example, the following is an entry off my website:

```YAML
title: SF Microservices Meetup - Going Serverless with Flask
author: Alex Miłowski
published: 2017-07-12T10:35:00-07:00
updated: 2017-07-12T10:35:00-07:00
keywords:
- python
- Flask
- Serverless
content: |
   I built a python package (see: [https://github.com/alexmilowski/flask-openwhisk](https://github.com/alexmilowski/flask-openwhisk)) for bridging between WSGI (Flask) and [OpenWhisk](http://openwhisk.incubator.apache.org). I have only tested it with Flask but it should work with
   other WSGI frameworks.

   The key takeaway is that you can deploy Flask applications with minimal changes on Serverless. Any
   changes that are necessary have to do with architectural changes for Serverless infrastructure. That
   typically comes from the fact that there is no local environment so configuration or
   local resources (e.g., files) need to be handled differently.
```

## Format Description

The following properties have specific meanings:

 * `title` (`schema:headline`)- the title of the entry.
 * `author` (`schema:author/schema:name` or list of) - the name of the author or a list of author names.
 * `published` (`schema:datePublished`) - the date the entry was published (ISO 8601)
 * `updated` (`schema:dateModified`) - the date the entry was published (ISO 8601)
 * `keywords` (mapped to `schema:keywords`) - a list of keywords associated with the entry
 * `description` (`schema:description`) - the description (summary) of the entry
 * `format` - (`schema:encodingFormat`) - the media type of the content.
 * `content` - (`schema:articleBody`) - the content of the blog entry (required)
 * `contentLocation` - (`schema:encoding/schema:contentUrl`) - the location of the content of the blog entry
 * `artifacts` - (a list of `schema:hasPart` or `schema:Collection`) - a set of local artifacts (e.g., images) associated with the entry
 * `genre` - (`schema:genre`) - a genre of the entry (e.g., summary, primary, etc.)
 * `summaryOf` - (`schema:isBasedOn`) - a url of a article/entry elsewhere of which this entry is a summary

The minimal entry is a single `content` property:

```YAML
content: |
   They've left me all alone. Where did everybody go?
```

Because YAML has some flexibility, properties like `author` can have a singular value:

```YAML
author: Son
content: |
   They've left me all alone. Where did everybody go?
```

or be a list of names:

```YAML
author:
- Son
- Foghorn Leghorn
content: |
   They've left me all alone. Where did everybody go?
```

Similarly, keywords are simply a list of keywords:

```YAML
author:
- Son
- Foghorn Leghorn
keywords:
- Merrie Melodies
- Mel Blanc
- Looney Tunes
- Ostrich
content: |
   They've left me all alone. Where did everybody go?
```

while schema.org expects a comma-separated value (e.g., `Merrie Melodies, Mel Blanc, Looney Tunes, Ostrich`).

Finally, properties can be in any order even though it is probably most convenient to have the `content` property last:

```YAML
author:
- Son
- Foghorn Leghorn
content: |
   They've left me all alone. Where did everybody go?
title: Mother was a rooster
```

is the same as:

```YAML
title: Mother was a rooster
author:
- Son
- Foghorn Leghorn
content: |
   They've left me all alone. Where did everybody go?
```


### Associated artifacts

When producing content for blog entries, there are often associated media and collections that are essential components to the content. These are listed via the `artifacts` property.  Each entry in the list should have a `kind` that indicates the media type of the artifact or a keyword value. The keyword `directory` indicates the location is a hierarchy of content (a directory).

The `location` property on the artifact specifies a relative URI of the content of the artifact. This may likely be a local or remote resource that is relative to the YAML file's base URI (if it has one).

### Encoding content

The entry content can be simply be embedded in the YAML by the `content` property:

```YAML
content: |
   They've left me all alone. Where did everybody go?
```

other formats will also easily embed:

```YAML
format: text/html
content: |
   <section>
   <p>They've left me all alone. Where did everybody go?</p>
   </section>
```

If you embed any content other than Markdown, you must specify a `format` property.

If the content of the entry is not embedded in the YAML, `contentLocation` can specify a relative URI of the content.

The `genre` can be used to control the classification of the content. For example, if any entry was a summary of a article posted on Medium:

```YAML
title: Mother was a rooster
author: Alex Miłowski
keywords:
- Merrie Melodies
- Mel Blanc
- Looney Tunes
- Ostrich
published: 2020-01-06T10:35:00-08:00
genre: summary
summaryOf: https://en.wikipedia.org/wiki/Mother_Was_a_Rooster
content: |
   They've left me all alone. Where did everybody go?
```

Note that the use of `genre` is subjective to the processing application as they translate to generic properties in the schema.org parlance.

### Other properties

Other properties can be embedded, including full schema.org properties, as long as they are legal YAML. Syntactically, a full property name can be embed by quoting the name:

```YAML
"http://schema.org/expires": 2019-01-07T10:11:00-07:00
```

or abbreviated CURIE names:
```YAML
"schema:expires": 2019-01-07T10:11:00-07:00
```

The processing of such properties depends on the receiving application's ability to handle JSON-LD or schema.org property syntax and interpretation.

## Parsing Entries

Firstly, the top-level syntax is [YAML](https://yaml.org). As such, you can use your favorite language and YAML package to read the metadata and content. For example, in Python you can use [PyYAML](https://pyyaml.org) as follows:

```Python
import yaml

with open('myentry.yaml') as file:
   metadata = yaml.load(file,Loader=yaml.Loader)

print(metadata['content'])
```

###  Processing Model

By default, there are some assumptions:

 * if there is no `format` property, the content is assumed to be Markdown
 * if there is no `published` property, the `updated` property is used
 * if there is no `updated` property, the current date and time is used.
 * A `title` property may be generated from the content (e.g., the first headline)
 * A `description` property may be generated from the content (e.g., the first paragraph)

### Python Library

This repository contains a python package for parsing the entries and transforming them into various formats: HTML, Turtle, JSON-LD. It implements the default processing model described above.

#### Loading an Article

Loading a simple entry is easy:

```Python
from yablog import Article

source = 'myentry.yaml'
with open(source) as file:
   entry = Article(source,baseuri=source)

print(entry.metadata['content'])
```

Articles have the following properties:

 * `metadata` - a mutable dictionary of metadata values
 * `baseuri` - the base URI of the article source

If the metadata data is changed, the `update()` method can be used to computed derived property values.

#### Converting to HTML

An article can be converted to HTML via the `toHTML()` method:

```Python
with open('output.html') as output:
   article.toHTML(output)
```

If your entries do not contain titles, you can generate the title from the `title` property:

```Python
with open('output.html') as output:
   article.toHTML(output,generateTitle=True)
```

Often, the source of the entry is not in the same location as the output resource. If you embed a `id` property, the resource location will default to that value. Otherwise, you can specify the resource location as well:

```Python
with open('1234.html') as output:
   article.toHTML(output,generateTitle=True,resource='http://www.example.com/entry/1234')
```

The default implementation of `transformContent()` provides the ability to convert from Markdown to HTML. For the ability to transform from other media types to HTML, you must subclass `Article` and override this method.

An example of the HTML output for the very first example is [available here](http://alexmilowski.github.io/milowski-journal/2017-07-12/sf-microservices-going-serverless.html).

#### Converting to Turtle

All the content except the `content` property can  be written in [Turtle](https://www.w3.org/TR/turtle/) via the `toTurtle()` method:

```Python
with open('output.ttl') as output:
   article.toTurtle(output)
```

The resource URI can be specified the same way as in the `toHTML()` method. Additionally, the HTML encoding can be generated via an `schema:associatedMedia` property via the `source` keyword:

```Python
with open('output.ttl') as output:
   article.toTurtle(output,source='http://www.example.com/content/entry/1234.html')
```

An example of the Turtle output for the very first example is [available here](http://alexmilowski.github.io/milowski-journal/2017-07-12/sf-microservices-going-serverless.ttl). Take note of how the turtle points to the HTML source.
