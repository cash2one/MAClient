#!/usr/bin/env python
# coding:utf-8
# maclient plugin loader and hooker
# Contributor:
#      fffonion        <fffonion@gmail.com>
import os,os.path as opath
import sys
import glob
#for plugin use
import urllib2
getPATH0=(opath.split(sys.argv[0])[1].find('py') != -1 or sys.platform=='cli') \
         and sys.path[0].decode(sys.getfilesystemencoding()) \
         or sys.path[1].decode(sys.getfilesystemencoding())#pyinstaller build
sys.path.append(opath.join(getPATH0,'plugins'))
#os.chdir(opath.join(getPATH0(),'plugins'))
#sys.path[0]=os.path.abspath(opath.join(getPATH0,'plugins'))
        
PREF_ENTER='ENTER_'
PREF_EXIT='EXIT_'
class plugins():
    def __init__(self,logger):
        self.logger=logger
        #所有插件模块对象
        self.plugins={}
        #所有插件模块中的plugin实例
        self.plugins_instance={}
        #新增cli命令字典
        self.extra_cmd={}
        #从maclient实例映射的变量
        self.val_dict={}
        self.load_plugins()
        #self.scan_hooks()
        self.enable=True
        

    def scan_hooks(self):
        self.hook_reg={}
        ALL_ACTIONS=['tasker','auto_check','check_strict_bc','set_card','red_tea','green_tea',
                    'explore','_explore_floor','gacha','select_card_sell','fairy_battle_loop','fairy_select','_fairy_battle',
                    'like','friends','reward_box','point_setting','factor_battle']
        #scan plugin hooks
        for p in self.plugins:
            #extra cmd
            ecmd=self._get_module_meta(p,'extra_cmd')
            for e in ecmd:
                hdl=self._get_module_meta(p,ecmd[e])
                if hdl:
                    self.extra_cmd[e]=hdl
            #function hook
            for act in ALL_ACTIONS:
                for method in [PREF_ENTER,PREF_EXIT]:#enter, exit
                    key='%s%s'%(method,act)
                    if key not in self.hook_reg:
                        self.hook_reg[key]={}
                    if key in self._get_module_meta(p,'hooks'):#add to hook reg
                        #priority record
                        self.hook_reg[key][p]=self._get_module_meta(p,'hooks')[key]  
    # def set_enable(self,lst):
    #     pass
    def set_maclient_val(self,val_dict):
        self.val_dict=val_dict

    def do_extra_cmd(self,cmd):
        if self.enable:
            return self.extra_cmd[cmd](self.val_dict)()
        else:
            self.logger.warning('Plugins not enabled.')

    def set_disable(self,lst):
        for p in lst:
            if p and (p in self.plugins):
                del(self.plugins[p])

    def _get_module_meta(self,mod,key):
        #module.xxx
        try:
           return getattr(self.plugins[mod],key)
        except AttributeError:
            self.logger.warning('"%s" not found in module "%s"'%(key,mod))
            return []

    def _get_plugin_attr(self,mod,attr):
        #module.plugin.xxx
        try:
           return getattr(self.plugins_instance[mod],attr)
        except AttributeError:
            self.logger.warning('Get "%s" failed from "%s" '%(attr,mod))
            return []

    def _do_hook(self,action,*args,**kwargs):
        if action in self.hook_reg:
            for plugin in sorted(self.hook_reg[action].iteritems(), key=lambda d:d[1], reverse = True):#high priority first
                f=self._get_plugin_attr(plugin[0],action)
                if f:
                    ret=f(*args, **kwargs)
                    if ret:#has mod on params
                        args,kwargs=ret
                        args=args[1:]#cut off caller instance variable
        return args,kwargs
    
    def load_plugins(self):
        import glob
        plugin_dir=opath.abspath(opath.join(getPATH0,'plugins'))
        mods=glob.glob(opath.join(plugin_dir,'*.py'))+\
            glob.glob(opath.join(plugin_dir,'*.pyc'))+\
            glob.glob(opath.join(plugin_dir,'*.pyo'))+\
            glob.glob(opath.join(plugin_dir,'*.pyd'))
        for m in mods:
            m=opath.splitext(opath.split(m)[1])[0]
            if m.startswith('_'):
                continue
            if m not in self.plugins:
                #module object
                self.plugins[m]=__import__(m)
                #plugin instance
                try:
                    self.plugins_instance[m]=self.plugins[m].plugin()
                except AttributeError:
                    #no plugin() class
                    self.plugins_instance[m]=None

    def _line_tracer(self):
        #originally from http://stackoverflow.com/questions/19227636/decorator-to-log-function-execution-line-by-line
        #it works almostly the same as module 'memory_profiler'
        #not working yet
        traced_func.add(func.func_code)
        def _wrapper(*args, **kwargs):#need a wrap
            old_trace_function = sys.gettrace()
            sys.settrace(logging_tracer)
            try:
                result = func(*args, **kwargs)
            except:
                raise
            else:
                return result
            finally:
                sys.settrace(old_trace_function)
        return _wrapper

    def func_hook(self,func):
        def do(*args, **kwargs):
            if self.enable:
                ret=self._do_hook('%s%s'%(PREF_ENTER,func.__name__),*args, **kwargs)
                args,kwargs=ret
                ret=func(*args, **kwargs)
                self._do_hook('%s%s'%(PREF_EXIT,func.__name__))
                return ret
            else:
                return func(*args, **kwargs)#passby
        return do

    def line_hook(self):
        pass

    # def __call__(self,func):
    #     return self.func_hook(func)

if __name__=='__main__':
    import maclient_logging
    p=plugins(maclient_logging.Logging('logging'))
    #p.set_disable(['hehe'])
    #print p.plugins,p.hook_reg
    class a():
        @p.func_hook
        def explore(a,b,c,d=1):
            print 1
    aa=a()
    aa.explore(1,2,3,d=3)
#!/usr/bin/env python
# coding:utf-8
# maclient plugin loader and hooker
# Contributor:
#      fffonion        <fffonion@gmail.com>
import os,os.path as opath
import sys
import glob
#for plugin use
import urllib2
getPATH0=(opath.split(sys.argv[0])[1].find('py') != -1 or sys.platform=='cli') \
         and sys.path[0].decode(sys.getfilesystemencoding()) \
         or sys.path[1].decode(sys.getfilesystemencoding())#pyinstaller build
sys.path.append(opath.join(getPATH0,'plugins'))
#os.chdir(opath.join(getPATH0(),'plugins'))
#sys.path[0]=os.path.abspath(opath.join(getPATH0,'plugins'))
        
PREF_ENTER='ENTER_'
PREF_EXIT='EXIT_'
class plugins():
    def __init__(self,logger):
        self.logger=logger
        #所有插件模块对象
        self.plugins={}
        #所有插件模块中的plugin实例
        self.plugins_instance={}
        #新增cli命令字典
        self.extra_cmd={}
        #从maclient实例映射的变量
        self.val_dict={}
        self.load_plugins()
        #self.scan_hooks()
        self.enable=True
        

    def scan_hooks(self):
        self.hook_reg={}
        ALL_ACTIONS=['tasker','auto_check','check_strict_bc','set_card','red_tea','green_tea',
                    'explore','_explore_floor','gacha','select_card_sell','fairy_battle_loop','fairy_select','_fairy_battle',
                    'like','friends','reward_box','point_setting','factor_battle']
        #scan plugin hooks
        for p in self.plugins:
            #extra cmd
            ecmd=self._get_module_meta(p,'extra_cmd')
            for e in ecmd:
                hdl=self._get_module_meta(p,ecmd[e])
                if hdl:
                    self.extra_cmd[e]=hdl
            #function hook
            for act in ALL_ACTIONS:
                for method in [PREF_ENTER,PREF_EXIT]:#enter, exit
                    key='%s%s'%(method,act)
                    if key not in self.hook_reg:
                        self.hook_reg[key]={}
                    if key in self._get_module_meta(p,'hooks'):#add to hook reg
                        #priority record
                        self.hook_reg[key][p]=self._get_module_meta(p,'hooks')[key]  
    # def set_enable(self,lst):
    #     pass
    def set_maclient_val(self,val_dict):
        self.val_dict=val_dict

    def do_extra_cmd(self,cmd):
        if self.enable:
            return self.extra_cmd[cmd](self.val_dict)()
        else:
            self.logger.warning('Plugins not enabled.')

    def set_disable(self,lst):
        for p in lst:
            if p and (p in self.plugins):
                del(self.plugins[p])

    def _get_module_meta(self,mod,key):
        #module.xxx
        try:
           return getattr(self.plugins[mod],key)
        except AttributeError:
            self.logger.warning('"%s" not found in module "%s"'%(key,mod))
            return []

    def _get_plugin_attr(self,mod,attr):
        #module.plugin.xxx
        try:
           return getattr(self.plugins_instance[mod],attr)
        except AttributeError:
            self.logger.warning('Get "%s" failed from "%s" '%(attr,mod))
            return []

    def _do_hook(self,action,*args,**kwargs):
        if action in self.hook_reg:
            for plugin in sorted(self.hook_reg[action].iteritems(), key=lambda d:d[1], reverse = True):#high priority first
                f=self._get_plugin_attr(plugin[0],action)
                if f:
                    ret=f(*args, **kwargs)
                    if ret:#has mod on params
                        args,kwargs=ret
                        args=args[1:]#cut off caller instance variable
        return args,kwargs
    
    def load_plugins(self):
        import glob
        plugin_dir=opath.abspath(opath.join(getPATH0,'plugins'))
        mods=glob.glob(opath.join(plugin_dir,'*.py'))+\
            glob.glob(opath.join(plugin_dir,'*.pyc'))+\
            glob.glob(opath.join(plugin_dir,'*.pyo'))+\
            glob.glob(opath.join(plugin_dir,'*.pyd'))
        for m in mods:
            m=opath.splitext(opath.split(m)[1])[0]
            if m.startswith('_'):
                continue
            if m not in self.plugins:
                #module object
                self.plugins[m]=__import__(m)
                #plugin instance
                try:
                    self.plugins_instance[m]=self.plugins[m].plugin()
                except AttributeError:
                    #no plugin() class
                    self.plugins_instance[m]=None

    def _line_tracer(self):
        #originally from http://stackoverflow.com/questions/19227636/decorator-to-log-function-execution-line-by-line
        #it works almostly the same as module 'memory_profiler'
        #not working yet
        traced_func.add(func.func_code)
        def _wrapper(*args, **kwargs):#need a wrap
            old_trace_function = sys.gettrace()
            sys.settrace(logging_tracer)
            try:
                result = func(*args, **kwargs)
            except:
                raise
            else:
                return result
            finally:
                sys.settrace(old_trace_function)
        return _wrapper

    def func_hook(self,func):
        def do(*args, **kwargs):
            if self.enable:
                ret=self._do_hook('%s%s'%(PREF_ENTER,func.__name__),*args, **kwargs)
                args,kwargs=ret
                ret=func(*args, **kwargs)
                self._do_hook('%s%s'%(PREF_EXIT,func.__name__))
                return ret
            else:
                return func(*args, **kwargs)#passby
        return do

    def line_hook(self):
        pass

    # def __call__(self,func):
    #     return self.func_hook(func)

if __name__=='__main__':
    import maclient_logging
    p=plugins(maclient_logging.Logging('logging'))
    #p.set_disable(['hehe'])
    #print p.plugins,p.hook_reg
    class a():
        @p.func_hook
        def explore(a,b,c,d=1):
            print 1
    aa=a()
    aa.explore(1,2,3,d=3)
    