import { useState, useEffect } from 'react';
import { Mic, Globe, Check, AlertCircle } from 'lucide-react';
import axios from 'axios';

interface Config {
  base_url: string;
  api_key: string;
  hotkey_asr: string;
  hotkey_translate_zh_en: string;
  hotkey_translate_en_zh: string;
}

declare global {
  interface Window {
    electronAPI: {
      getConfig: () => Promise<Config>;
      saveConfig: (config: Partial<Config>) => Promise<boolean>;
      setRecording: (status: boolean) => Promise<void>;
      writeClipboard: (text: string) => Promise<void>;
      onRecordingStatus: (callback: (status: boolean) => void) => void;
    };
  }
}

function App() {
  const [config, setConfig] = useState<Config>({
    base_url: 'http://localhost:3456',
    api_key: '',
    hotkey_asr: 'alt',
    hotkey_translate_zh_en: 'shift',
    hotkey_translate_en_zh: 'shift+a'
  });
  const [isRecording, setIsRecording] = useState(false);
  const [saved, setSaved] = useState(false);
  const [status, setStatus] = useState<string>('');

  useEffect(() => {
    window.electronAPI.getConfig().then(setConfig);
    window.electronAPI.onRecordingStatus((status) => {
      setIsRecording(status);
      if (status) {
        setStatus('录音中...');
      }
    });
  }, []);

  const handleSave = async () => {
    await window.electronAPI.saveConfig(config);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const testConnection = async () => {
    try {
      setStatus('测试连接中...');
      await axios.get(`${config.base_url}/health`);
      setStatus('连接成功!');
    } catch (e) {
      setStatus('连接失败，请检查Host服务');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-md mx-auto bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-5">
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Mic className="w-6 h-6" />
            SpeechMate
          </h1>
          <p className="text-blue-100 text-sm mt-1">语音识别 & 翻译助手</p>
        </div>

        <div className="p-5 space-y-4">
          <div className={`flex items-center justify-center p-4 rounded-lg ${isRecording ? 'bg-red-50 animate-pulse' : 'bg-gray-50'}`}>
            <Mic className={`w-8 h-8 ${isRecording ? 'text-red-500' : 'text-gray-400'}`} />
            <span className={`ml-2 font-medium ${isRecording ? 'text-red-600' : 'text-gray-500'}`}>
              {isRecording ? '录音中...' : '等待录音'}
            </span>
          </div>

          {status && (
            <div className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 p-2 rounded">
              <AlertCircle className="w-4 h-4" />
              {status}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Base URL</label>
            <input
              type="text"
              value={config.base_url}
              onChange={(e) => setConfig({ ...config, base_url: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="http://localhost:3456"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
            <input
              type="password"
              value={config.api_key}
              onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="sk-xxx"
            />
          </div>

          <button
            onClick={testConnection}
            className="w-full py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium text-gray-700"
          >
            测试连接
          </button>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">快捷键配置</label>
            <div className="bg-gray-50 rounded-lg p-3 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="flex items-center gap-1"><Mic className="w-3 h-3"/> 语音识别:</span>
                <kbd className="px-2 py-1 bg-white rounded border text-xs">{config.hotkey_asr}</kbd>
              </div>
              <div className="flex justify-between">
                <span className="flex items-center gap-1"><Globe className="w-3 h-3"/> 中→英:</span>
                <kbd className="px-2 py-1 bg-white rounded border text-xs">{config.hotkey_translate_zh_en}</kbd>
              </div>
              <div className="flex justify-between">
                <span className="flex items-center gap-1"><Globe className="w-3 h-3"/> 英→中:</span>
                <kbd className="px-2 py-1 bg-white rounded border text-xs">{config.hotkey_translate_en_zh}</kbd>
              </div>
            </div>
          </div>

          <button
            onClick={handleSave}
            className={`w-full py-3 rounded-lg font-medium transition-all ${
              saved ? 'bg-green-500 text-white' : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700'
            }`}
          >
            {saved ? <span className="flex items-center justify-center gap-2"><Check className="w-5 h-5" /> 已保存</span> : '保存设置'}
          </button>
        </div>

        <div className="bg-gray-50 px-5 py-3 text-center text-xs text-gray-500">
          Alt: 识别 | Shift: 中→英 | Shift+A: 英→中
        </div>
      </div>
    </div>
  );
}

export default App;
