import argparse
import os
import shutil

from yamlblog import Article, Publisher
from yamlblog import generate


class ArticleConverter:
   def __init__(self,weburi,entryuri):
      self.weburi = weburi
      self.entryuri = [ entryuri ]

   def enter(self,suffix):
      self.entryuri.append(self.entryuri[-1] + suffix)

   def leave(self):
      return self.entryuri.pop()

def isoformat(s):
   return s if type(s)==str else s.isoformat()

def updateNeeded(source,target,force=False):
   updatedNeeded = force or not(os.path.exists(target))
   if not updatedNeeded:
      btime = os.path.getmtime(source)
      updatedNeeded = btime > os.path.getmtime(target)
   return updatedNeeded


def main():
   argparser = argparse.ArgumentParser(description='Article HTML and Turtle Generator')
   argparser.add_argument('-f',action='store_true',help='Forces all the files to be regenerated.',dest='force')
   argparser.add_argument('--extension',nargs='?',help='The source file extension',default='md')
   argparser.add_argument('-o',nargs='?',help='The output directory',dest='outdir')
   argparser.add_argument('-w',nargs='?',help='The web uri',dest='weburi',default='http://www.milowski.com/journal/entry/')
   argparser.add_argument('-e',nargs='?',help='The entry uri directory',dest='entryuri',default='http://alexmilowski.github.io/milowski-journal/')
   argparser.add_argument('--publisher',nargs='?',help='The publisher')
   argparser.add_argument('dir',nargs=1,help='The directory to process.')
   argparser.add_argument('--single',action='store_true',default=False,help='Process a single directory')
   argparser.add_argument('--turtle',action='store_true',default=False,help='Generate turtle output')
   argparser.add_argument('--cypher',action='store_true',default=False,help='Generate cypher output')
   argparser.add_argument('--html',action='store_true',default=False,help='Generate html output')
   argparser.add_argument('--merge',action='store_true',default=False,help='Use Cypher merge instead of create.')
   args = argparser.parse_args()
   inDir = args.dir[0]
   outDir = args.outdir if (args.outdir!=None) else inDir
   same = inDir==outDir
   if outDir[-1]==os.sep:
      outDir = outDir[0:-1]
   if args.single:
      if inDir[-1]==os.sep:
         inDir = inDir[0:-1]
      last = inDir.rfind(os.sep)
      if last<0:
         dirs = [inDir]
         inDir = '.'
         if not same:
            outDir = outDir + os.sep + inDir
         else:
            outDir = '.'
      else:
         dirs = [inDir[last+1:]]
         inDir = inDir[0:last]
         if inDir=='':
            inDir = '/'
         if same:
            outDir = inDir
   else:
      dirs = [d for d in os.listdir(inDir) if not(d[0]=='.') and os.path.isdir(inDir + '/' + d)]

   publisher = None
   if args.publisher is not None:
      with open(args.publisher) as source:
         publisher = Publisher(source)

   converter = ArticleConverter(args.weburi,args.entryuri)

   extension = '.' + args.extension if args.extension[0]!='.' else args.extension
   extension_count = extension.count('.')

   for dir in dirs:

      sourceDir = inDir + '/' + dir
      targetDir = outDir + '/' + dir

      print(sourceDir+':')

      if (not(os.path.exists(targetDir))):
         os.makedirs(targetDir)

      converter.enter(dir+'/')

      files = [f for f in os.listdir(sourceDir) if f.endswith(extension) and os.path.isfile(sourceDir + '/' + f)]

      for file in files:

         sourceFile = sourceDir + '/' + file
         base = file.rsplit('.',extension_count)[0]

         with open(sourceFile) as source:
            article = Article(source,baseuri=sourceFile,publisher=publisher)
            resource = converter.weburi + isoformat(article.metadata['published'])
            entry = converter.entryuri[-1] + base + '.html'

            if args.html:
               htmlFile = targetDir + '/' + base + ".html"
               if updateNeeded(sourceFile,htmlFile,force=args.force):
                  print(file + " → " + htmlFile)
                  with open(htmlFile,'w') as output:
                     generate(article,'text/html',output,generateTitle=True,resource=resource)
            if args.turtle:
               turtleFile = targetDir + '/' + base + ".ttl"
               if updateNeeded(sourceFile,turtleFile,force=args.force):
                  print(file + " → " + turtleFile)
                  with open(turtleFile,'w') as output:
                     generate(article,'text/html',output,resource=resource,source=entry)
            if args.cypher:
               cypherFile = targetDir + '/' + base + ".cypher"
               if updateNeeded(sourceFile,cypherFile,force=args.force):
                  print(file + " → " + cypherFile)
                  with open(cypherFile,'w') as output:
                     generate(article,'text/x.cypher',output,resource=resource,source=entry,useMerge=args.merge)

      if same:
         continue
      work = [f for f in os.listdir(sourceDir) if (not f.endswith('.md'))]
      for file in work:
         sourceFile = sourceDir + '/' + file
         targetFile = targetDir + '/' + file
         if os.path.isfile(sourceFile):
            copyNeeded = updateNeeded(sourceFile,targetFile,force=args.force)

            if copyNeeded:
               print(file + " → " + targetFile)
               shutil.copyfile(sourceFile,targetFile)
         elif os.path.isdir(sourceFile):
            if os.path.exists(targetFile):
               print('sync tree ' + sourceFile)
               work += [sourceFile + '/' + f for f in os.listdir(sourceFile)]
            else:
               print("copy tree " + sourceFile + " → " + targetFile)
               shutil.copytree(sourceFile,targetFile)

      converter.leave()

if __name__ == '__main__':
   main()
