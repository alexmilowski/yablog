import argparse
import os
import shutil

from yablog import Article


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


def main():
   argparser = argparse.ArgumentParser(description='Article HTML and Turtle Generator')
   argparser.add_argument('-f',action='store_true',help='Forces all the files to be regenerated.',dest='force')
   argparser.add_argument('--extension',nargs='?',help='The source file extension',default='md')
   argparser.add_argument('-o',nargs='?',help='The output directory',dest='outdir')
   argparser.add_argument('-w',nargs='?',help='The web uri',dest='weburi',default='http://www.milowski.com/journal/entry/')
   argparser.add_argument('-e',nargs='?',help='The entry uri directory',dest='entryuri',default='http://alexmilowski.github.io/milowski-journal/')
   argparser.add_argument('dir',nargs=1,help='The directory to process.')
   argparser.add_argument('--no-turtle',dest='turtle',action='store_false',default=True,help='Do not generate turtle')
   args = argparser.parse_args()
   inDir = args.dir[0]
   outDir = args.outdir if (args.outdir!=None) else inDir
   dirs = [d for d in os.listdir(inDir) if not(d[0]=='.') and os.path.isdir(inDir + '/' + d)]

   converter = ArticleConverter(args.weburi,args.entryuri)

   extension = '.' + args.extension if args.extension[0]!='.' else args.extension
   extension_count = extension.count('.')

   for dir in dirs:

      sourceDir = inDir + '/' + dir
      targetDir = outDir + '/' + dir

      if (not(os.path.exists(targetDir))):
         os.makedirs(targetDir)

      converter.enter(dir+'/')

      files = [f for f in os.listdir(sourceDir) if f.endswith(extension) and os.path.isfile(sourceDir + '/' + f)]

      for file in files:

         targetFile = sourceDir + '/' + file
         base = file.rsplit('.',extension_count)[0]
         htmlFile = targetDir + '/' + base + ".html"
         turtleFile = targetDir + '/' + base + ".ttl"

         updatedNeeded = args.force or not(os.path.exists(htmlFile)) or not(os.path.exists(turtleFile))
         if (not(updatedNeeded)):
            btime = os.path.getmtime(targetFile)
            updatedNeeded = btime > os.path.getmtime(htmlFile) or btime > os.path.getmtime(turtleFile)

         if (not(updatedNeeded)):
            continue

         print(file + " → " + htmlFile + ", " + turtleFile)

         with open(targetFile) as file, open(htmlFile,'w') as html:
            article = Article(file,baseuri=targetFile)
            resource = converter.weburi + isoformat(article.metadata['published'])

            article.toHTML(html,generateTitle=True,resource=resource)
            if args.turtle:
               with open(turtleFile,'w') as turtle:
                  entry = converter.entryuri[-1] + base + '.html'
                  article.toTurtle(turtle,resource=resource,source=entry)


      work = [f for f in os.listdir(sourceDir) if (not f.endswith('.md'))]
      for file in work:
         sourceFile = sourceDir + '/' + file
         targetFile = targetDir + '/' + file
         if os.path.isfile(sourceFile):
            copyNeeded = args.force or not(os.path.exists(targetFile)) or os.path.getmtime(sourceFile) > os.path.getmtime(targetFile)

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
