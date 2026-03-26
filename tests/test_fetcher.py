import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from data.fetcher import DataFetcher
from utils.exceptions import DataFetchException


def test_fetcher_initialization():
    """Test DataFetcher can be initialized"""
    fetcher = DataFetcher()
    assert fetcher is not None
    assert fetcher.use_cache is True
    assert fetcher.max_retries == 3
    assert fetcher.retry_delay == 1.0


@patch('akshare.stock_board_industry_name_em')
def test_get_industry_sectors(mock_api):
    """Test getting industry sectors"""
    mock_df = pd.DataFrame({
        '板块名称': ['银行', '科技'],
        '板块代码': ['BK0001', 'BK0002']
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher()
    result = fetcher.get_industry_sectors()

    assert not result.empty
    assert '板块名称' in result.columns
    assert '板块代码' in result.columns


@patch('akshare.stock_board_concept_name_em')
def test_get_concept_sectors(mock_api):
    """Test getting concept sectors"""
    mock_df = pd.DataFrame({
        '板块名称': ['人工智能', '新能源'],
        '板块代码': ['BK0010', 'BK0020']
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher()
    result = fetcher.get_concept_sectors()

    assert not result.empty
    assert '板块名称' in result.columns
    assert '板块代码' in result.columns


@patch('akshare.stock_board_industry_cons_em')
def test_get_sector_stocks_industry(mock_api):
    """Test getting industry sector stocks"""
    mock_df = pd.DataFrame({
        '代码': ['000001', '000002'],
        '名称': ['平安银行', '万科A']
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher()
    result = fetcher.get_sector_stocks('银行', 'industry')

    assert not result.empty
    assert '代码' in result.columns
    assert '名称' in result.columns


@patch('akshare.stock_board_concept_cons_em')
def test_get_sector_stocks_concept(mock_api):
    """Test getting concept sector stocks"""
    mock_df = pd.DataFrame({
        '代码': ['000001', '000002'],
        '名称': ['平安银行', '万科A']
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher()
    result = fetcher.get_sector_stocks('人工智能', 'concept')

    assert not result.empty
    assert '代码' in result.columns
    assert '名称' in result.columns


@patch('akshare.stock_individual_info_em')
def test_get_stock_info(mock_api):
    """Test getting stock info"""
    mock_data = {
        '股票简称': '平安银行',
        '行业': '银行',
        '上市日期': '1991-04-03'
    }
    mock_api.return_value = mock_data

    fetcher = DataFetcher()
    result = fetcher.get_stock_info('000001.SZ')

    assert result['股票简称'] == '平安银行'
    assert result['行业'] == '银行'


@patch('akshare.stock_individual_info_em')
def test_get_stock_info_without_suffix(mock_api):
    """Test getting stock info without exchange suffix"""
    mock_data = {
        '股票简称': '平安银行',
        '行业': '银行',
        '上市日期': '1991-04-03'
    }
    mock_api.return_value = mock_data

    fetcher = DataFetcher()
    result = fetcher.get_stock_info('000001')

    assert result['股票简称'] == '平安银行'


@patch('akshare.stock_individual_info_em')
def test_get_stock_info_dataframe_format(mock_api):
    """Test getting stock info when API returns DataFrame"""
    mock_df = pd.DataFrame({
        'item': ['股票简称', '行业', '上市日期'],
        'value': ['平安银行', '银行', '1991-04-03']
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher()
    result = fetcher.get_stock_info('000001')

    assert isinstance(result, dict)


@patch('akshare.stock_zh_a_hist')
def test_get_stock_history(mock_api):
    """Test getting stock history"""
    mock_df = pd.DataFrame({
        '日期': ['2024-01-01', '2024-01-02'],
        '开盘': [10.0, 10.5],
        '最高': [10.5, 11.0],
        '最低': [9.8, 10.2],
        '收盘': [10.3, 10.8],
        '成交量': [1000000, 1200000]
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher()
    result = fetcher.get_stock_history('000001.SZ', '2024-01-01')

    assert not result.empty
    assert '开盘' in result.columns
    assert '收盘' in result.columns
    assert '成交量' in result.columns


@patch('akshare.stock_zh_a_hist')
def test_get_stock_history_with_date_range(mock_api):
    """Test getting stock history with date range"""
    mock_df = pd.DataFrame({
        '日期': ['2024-01-01', '2024-01-02'],
        '开盘': [10.0, 10.5],
        '最高': [10.5, 11.0],
        '最低': [9.8, 10.2],
        '收盘': [10.3, 10.8],
        '成交量': [1000000, 1200000]
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher()
    result = fetcher.get_stock_history('000001.SZ', '2024-01-01', '2024-01-31')

    assert not result.empty


@patch('akshare.stock_zh_a_spot_em')
def test_get_stock_latest(mock_api):
    """Test getting latest stock data"""
    mock_df = pd.DataFrame({
        '代码': ['000001', '000002'],
        '名称': ['平安银行', '万科A'],
        '最新价': [10.5, 15.2],
        '涨跌幅': [0.5, -0.3]
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher()
    result = fetcher.get_stock_latest('000001.SZ')

    assert '最新价' in result
    assert result['代码'] == '000001'
    assert result['名称'] == '平安银行'


@patch('akshare.stock_zh_a_spot_em')
def test_get_stock_latest_not_found(mock_api):
    """Test getting latest stock data when stock not found"""
    mock_df = pd.DataFrame({
        '代码': ['000002'],
        '名称': ['万科A'],
        '最新价': [15.2],
        '涨跌幅': [-0.3]
    })
    mock_api.return_value = mock_df

    # Disable cache to ensure we test the actual failure
    fetcher = DataFetcher(use_cache=False)
    with pytest.raises(DataFetchException):
        fetcher.get_stock_latest('000001.SZ')


@patch('akshare.stock_board_industry_name_em')
def test_retry_logic_success(mock_api):
    """Test that retry logic works on success"""
    mock_df = pd.DataFrame({
        '板块名称': ['银行'],
        '板块代码': ['BK0001']
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher(max_retries=3)
    result = fetcher.get_industry_sectors()

    assert not result.empty


@patch('akshare.stock_board_industry_name_em')
def test_retry_logic_failure(mock_api):
    """Test that retry logic raises exception after all retries"""
    mock_api.side_effect = Exception("API Error")

    # Disable cache to ensure we test the actual failure
    fetcher = DataFetcher(use_cache=False, max_retries=2)
    with pytest.raises(DataFetchException):
        fetcher.get_industry_sectors()


def test_no_cache_initialization():
    """Test DataFetcher initialization without cache"""
    fetcher = DataFetcher(use_cache=False)
    assert fetcher is not None
    assert fetcher.use_cache is False
    assert fetcher.cache is None


@patch('akshare.stock_board_industry_name_em')
def test_cache_integration(mock_api):
    """Test that cache is properly integrated"""
    mock_df = pd.DataFrame({
        '板块名称': ['银行'],
        '板块代码': ['BK0001']
    })
    mock_api.return_value = mock_df

    fetcher = DataFetcher(use_cache=True)

    # First call - should hit API
    result1 = fetcher.get_industry_sectors()
    assert not result1.empty

    # Second call - should hit cache (mock should not be called again)
    mock_api.reset_mock()
    result2 = fetcher.get_industry_sectors()
    assert not result2.empty