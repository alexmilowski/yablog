# yablog

A simple YAML-based blog entry format.

## Motivation

In 2016, I was motivated to make my blog and website easier. I wanted to use "Semantic Web" technology and drive the blog for my website and other content by the "linked data graph". That project, called [duckpond](https://github.com/alexmilowski/duckpond/) worked well.

During the process, I wanted a simple authoring format where I could use github to store my blog entries and associated artifacts safely. Markdown seemed like a good choice except that I also needed a way to author the metadata. Originally, I settled on a simple header format of key/values. Ultimately, this has evolved into the use of YAML.

Turns out that Markdown nicely embeds into YAML. So does a lot of other formats. Who knew?

## An Example

Every entry parses as a YAML file. The essential metadata map nicely to a [schema.org BlogPosting](http://schema.org/BlogPosting) type although the properties are not named extactly the same.  For example, the following is an entry off my website.

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

 * `title` (`schema:headline`)- the title of the entry. If there is not title, the converter will attempt to generate one from the content.
 * `author` (`schema:author/schema:name` or list of) - the name of the author or a list of author names.
 * `published` (`schema:datePublished`) - the date the entry was published. If omitted, it defaults to updated.
 * `updated` (`schema:dateModified`) - the date the entry was published. If omitted, it defaults to the current date and time.
 * `keywords` (mapped to `schema:keywords`) - a list of keywords associated with the entry
 * `format` - (`schema:encodingFormat`) - the media type of the content. If omitted, it defaults to text/markdown.
 * `content` - (`schema:articleBody`) - the content of the blog entry.
 * `contentLocation` - (`schema:encoding/schema:contentUrl`) - the location of the content of the blog entry
 * `artifacts` - (a list of `schema:associatedMedia` or `schema:Collection`) - a set of local artifacts (e.g., images) associated with the entry
 * `genre` - (`schema:genre`) - a genre of the entry (e.g., summary, primary, etc.)
 * `summaryOf` - (`schema:isBasedOn`) - a url of a article/entry elsewhere of which this entry is a summary

Because YAML has some flexibility, properties like `author` can have a singular value:

```YAML
author: Alex Miłowski
```

or be a list of names:

```YAML
author:
   - Alex Miłowski
   - Elvis
```

Similarly, keywords are simply a list of keywords:

```YAML
keywords:
- python
- Flask
- Serverless
```

while schema.org expects a comma-separated value (e.g., `python, Flask, Serverless`).

### Associated artifacts

When producing content for blog entries, there are often associated media and collections that are essential components to the content. These are listed via the `artifacts` property.  Each entry in the list should have a `kind` that indicates the media type of the artifact. The special value of `directory` indicates the location is a hierarchy of content (a directory).

The `location` property on the artifact specifices a relative URI of the content of the artifact. This may likely be a local file or directory relative to the YAML file's base URI.

### Encoding content

The entry content can be simply be embedded in the YAML by the `content` property:

```YAML
content: |
   I am some markdown `text`!
```

other formats will also easily embed:

```YAML
format: text/html
content: |
   <section>
   <p>Here is some HTML!</p>
   </section>
```

If you embed any content other than Markdown, you must specify a `format` property.

If the content of the entry is not embedded in the YAML, `contentLocation` can specify a relative URI of the content.

The `genre` can be used to control the classification of the content. For example, if any entry was a summary of a article posted on Medium:

```YAML
title: My Dog is a Sea Wolf
author: Alex Miłowski
published: 2020-01-06T10:35:00-08:00
keywords:
- dogs
genre: summary
summaryOf: http://www.medium.com/...
content: |
   My dog is secretly a Sea Wolf. Really. It's true!
```

Note that the use of `genre` is subjective to the processing application as they translate to generic properties in the schema.org parlance.

### Other properties

## Parsing with Python

This repository contains a python package for parsing the entries and transforming them into various formats: HTML, Turtle, JSON-LD.
